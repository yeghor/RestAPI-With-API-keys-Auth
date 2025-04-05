from fastapi import FastAPI, Body, Depends, Header, HTTPException, Query, Path
from typing import List, Dict, Any, Optional, Annotated
from schemas import UserSchema, UserBase
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

app = FastAPI()
Base.metadata.create_all(bind=engine)

def read_config_expiery_hours() -> str:
    config = configparser.ConfigParser()

    config.read(os.path.join("config.ini"))
    return config.get("General", "jwt_token_expiery_hours")

def jwt_token_authorization(username, jwt_token) -> bool:
    db = session_local()
    if db.query(JWTs).filter(JWTs.username == username, JWTs.jwt_token == jwt_token).first():
        db.close()
        return True
    else:
        db.close()
        False

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
    
    return {
        "detail": f"New user ({user.username}) succesfuly created. DON'T LOSE YOUR API KEY FOLLOWED BELOW",
        "api_key": user.api_key
    }


@app.post("/auth/")
def auth(username = Header(...), api_key = Header(...), db: Session = Depends(get_db)) -> dict:
    token_expiery = int(read_config_expiery_hours())

    user = db.query(Users).filter(Users.username == username).first()
    
    if not user:
        raise HTTPException(status_code=404, detail=f"Not found any registered username: {username}")

    if user.api_key == api_key:
        jwt_token = encode_jwt(username=username, api_key=api_key)
        existing_token: JWTs = db.query(JWTs).filter(JWTs.username == username).first()
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

        timestamp = datetime.now()
        expires_at = timestamp + timedelta(hours=token_expiery)
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

@app.get("/user_info/{username}/{auth_token}")
def get_user_info(
    username: Annotated[str, Path(title="Username", example="User-1", min_length=3, max_length=50)],
    auth_token: Annotated[str, Path(title="Your work API token", example="eyJhbv...RwIrjXM")],
    db: Session = Depends(get_db),
    ):
    if jwt_token_authorization(username=username, jwt_token=auth_token):
        return db.query(Users).filter(Users.username == username).first()
    else:
        raise HTTPException(status_code=401, detail="Unauthorized acces")