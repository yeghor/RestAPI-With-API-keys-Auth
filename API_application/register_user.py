from sqlalchemy.orm import Session
from database import session_local, Base, engine
from datetime import date
from models import Users
from construct_unique_api_key import generate_api_key
from main import UserSchema
from exceptions import UsernameAlreadyExists

def register_new_user(username) -> UserSchema:
    if any(char in username for char in ["@","!","?","$","#","%","^","&","(",")","[","]","{","}",";",":",">","<","№","|",]):
        raise ValueError("Username contains not allowed chars")
    if len(username) < 3:
        raise ValueError("Username length must be at least 3 characters")
    Base.metadata.create_all(engine)
    try:
        db = session_local()
        if db.query(Users).filter(Users.username == username).first():
            raise UsernameAlreadyExists("User with this username allready exists")

        datestamp = str(date.today())
        api_key = generate_api_key()
        user = Users(api_key=api_key, username=username, date_joined=datestamp, requests=0)
        db.add(user)
        db.commit()
        db.refresh(user)

        user_dict = {
            "api_key": user.api_key,
            "username": user.username,
            "date_joined": user.date_joined,
            "requests": user.requests
        }

        return UserSchema(**user_dict)
    finally:
        db.close()