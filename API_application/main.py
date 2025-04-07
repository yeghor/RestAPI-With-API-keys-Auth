from fastapi import FastAPI, Body, Depends, Header, HTTPException, Query, Path
from typing import List, Dict, Any, Optional, Annotated
from schemas import UserSchema, UserBase, JWTTokenReturn, TitanicPassenger
from construct_unique_api_key import generate_api_key
from sqlalchemy.orm import Session
from database import session_local, Base, engine
from models import Users, JWTs
from database import Base
from exceptions import UsernameAlreadyExists
from jwt_token import encode_jwt
from register_user import register_new_user
from datetime import datetime, timedelta
import configparser
import os
import random
import json

app = FastAPI()
Base.metadata.create_all(bind=engine)

def read_config_expiery_hours() -> str:
    config = configparser.ConfigParser()

    config.read(os.path.join("config.ini"))
    return config.get("General", "jwt_token_expiery_hours")

def jwt_token_authorization(user: Users, jwt_token: str, db: Session) -> bool:
    token = db.query(JWTs).filter(JWTs.username == user.username, JWTs.jwt_token == jwt_token).first()

    if not token:
        return None
    if datetime.now() > token.expires_at:
        return False
    return bool(user)

def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def test() -> Dict:
    return {"detail": "Hello World"}

@app.post("/register/")
def register(username = Header(...), db: Session = Depends(get_db)) -> UserBase:
    try:
        user = register_new_user(username=username)
    except ValueError:
        raise HTTPException(status_code=401, detail="Username length must be at least 3 characters and must not containt any folowing characters: @,!,?,$,#,%,^,&,(,),[,],{,},;,:,>,<,№,|")
    except UsernameAlreadyExists:
        raise HTTPException(status_code=401, detail="This username already taken")
    
    user_collection = {
            "username": user.username,
            "api_key": user.api_key,
        }  

    return UserBase(**user_collection)


@app.post("/auth/")
def auth(username = Header(...), api_key = Header(...), db: Session = Depends(get_db)) -> JWTTokenReturn:
    token_expiery = int(read_config_expiery_hours())

    user = db.query(Users).filter(Users.username == username).first()
    
    if not user:
        raise HTTPException(status_code=404, detail=f"Not found any registered username: {username}")

    timestamp = datetime.now()
    expires_at = timestamp + timedelta(hours=token_expiery)

    if user.api_key == api_key:
        jwt_token = encode_jwt(username=username)
        existing_token: JWTs = db.query(JWTs).filter(JWTs.username == username, JWTs.jwt_token == jwt_token).first()
        if existing_token:
            if datetime.now() < existing_token.expires_at:
                return {
                    "detail": "You're already authorized",
                    "authorization_token": existing_token.jwt_token,
                    "issued_at": existing_token.issued_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "expires_at": existing_token.expires_at.strftime("%Y-%m-%d %H:%M:%S"),
                    }
            else:
                db.delete(existing_token)
                db.commit()
                raise HTTPException(status_code=403, detail="Token expired")
            
        db.add(JWTs(username=username, jwt_token=jwt_token, expires_at=expires_at))
        db.commit()
        return {
            "detail": f"Your authorization token. Expires in {token_expiery} hours",
            "authorization_token": jwt_token,
            "issued_at": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "expires_at": expires_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
    else:
        raise HTTPException(status_code=401, detail="Unauthorized access")
    
@app.get("/user_info/{username}")
def get_user_info(
    username: Annotated[str, Path(..., title="Username", example="User-1", min_length=3, max_length=50)],
    auth_token: Annotated[str, Header(..., title="Your work API token", example="eyJhbv...RwIrjXM")],
    db: Session = Depends(get_db),
    ) -> UserSchema:
    
    user =  db.query(Users).filter(Users.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized acces")
    
    if jwt_token_authorization(user=user, jwt_token=auth_token, db=db):
        user.requests += 1
        user_collection = {
            "username": user.username,
            "api_key": user.api_key,
            "date_joined": user.date_joined,
            "requests": user.requests
        }
        db.commit()
        return UserSchema(**user_collection)
    else:
        raise HTTPException(status_code=401, detail="Unauthorized acces")
    
@app.get("/delete_account/")
def delete_account(
    username = Annotated[str, Header(..., title="Username", example="User-1", min_length=3, max_length=50)],
    api_key = Annotated[str, Header(..., title="Your personal api_key")],
    db: Session = Depends(get_db),
    ) -> UserSchema:
    user: Users = db.query(Users).filter(Users.username == username, Users.api_key == api_key).first()
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized acces")
    db.delete(user) 
    user_collection = {
            "username": user.username,
            "api_key": user.api_key,
            "date_joined": user.date_joined,
            "requests": user.requests
        }    
   
    db.commit()

    return UserSchema(**user_collection)

@app.get("/random_titanic_passenger/")
def get_passenget(
    username: Annotated[str, Header(..., title="Username", example="User-1", min_length=3, max_length=50)],
    auth_token: Annotated[str, Header(..., title="Your work API token", example="eyJhbv...RwIrjXM")],
    db: Session = Depends(get_db)
    ) -> TitanicPassenger:
    user = db.query(Users).filter(Users.username == username).first()
    if jwt_token_authorization(jwt_token=auth_token, db=db, user=user):
        user.requests += 1
        db.commit()
        filepath = os.path.join("titanic.json")
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
            data_pass = data[random.randint(0, len(data))]
            print(data_pass)
            return TitanicPassenger(**data_pass)
    else:
        raise HTTPException(status_code=401, detail="Unauthorized acces")