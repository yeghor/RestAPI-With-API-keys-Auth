from fastapi import FastAPI, Body, Depends, Header, HTTPException
from typing import List, Dict, Any, Optional, Annotated
from schemas import UserSchema
from construct_unique_api_key import generate_api_key
from sqlalchemy.orm import Session
from database import session_local, Base, engine
from models import Users
from database import Base
from exceptions import UsernameAlreadyExists
from jwt_token import encode_jwt
import json
from register_user import register_new_user
app = FastAPI()
Base.metadata.create_all(bind=engine)

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
def register(username = Header(...), db: Session = Depends(get_db)) -> Dict:
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
    try:
        user = db.query(Users).filter(Users.username == username).first()
    except ValueError:
        raise HTTPException(status_code=401, detail="Username length must be at least 3 characters and must not containt any folowing characters: @,!,?,$,#,%,^,&,(,),[,],{,},;,:,>,<,№,|")
    except UsernameAlreadyExists:
        raise HTTPException(status_code=401, detail="This username already taken")

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.api_key == api_key:
        jwt_token = encode_jwt(username=username, api_key=api_key)
        with open("authorized_jwts.json", "r") as file:
            jwts = json.load(file)
            token = {"token":jwt_token, "username":username}
            for item in jwts['tokens']:
                if item["token"] == token["token"] and item["username"] == username:
                    return {
                        "detail": "Youre already authorized",
                        "authorization_token": jwt_token
                    }
            
            jwts["tokens"].append(token)

            with open("authorized_jwts.json", "w") as file:              
                json.dump(jwts, file, indent=4)
        return {
            "detail": "Your authorization token",
            "authorization_token": jwt_token
            }
    else:
        raise HTTPException(status_code=401, detail="Unauthorized acces")
