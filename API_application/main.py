from fastapi import FastAPI, Body, Depends, Header, HTTPException
from typing import List, Dict, Any, Optional, Annotated
from schemas import UserSchema
from construct_unique_api_key import generate_api_key
from sqlalchemy.orm import Session
from database import session_local, Base, engine
from models import Users
from database import Base
from exceptions import UsernameAlreadyExists
from jwt_token import construct_jwt

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
def get_api_key(username = Header(), db: Session = Depends(get_db)) -> Optional[UserSchema]:
    try:
        user = db.query(Users).filter(Users.username == username).first()
    except ValueError:
        raise HTTPException(status_code=401, detail="Username length must be at least 3 characters and must not containt any folowing characters: @,!,?,$,#,%,^,&,(,),[,],{,},;,:,>,<,№,|")
    except UsernameAlreadyExists:
        ra

@app.post("/auth/")
def auth(username = Header(...), api_key = Header(...), db: Session = Depends(get_db)):
    pass