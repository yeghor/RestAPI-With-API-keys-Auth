from fastapi import FastAPI, Body, Depends, Header
from typing import List, Dict, Any, Optional, Annotated
from schemas import Stats, UserSchema
from construct_unique_api_key import generate_api_key
from sqlalchemy.orm import Session
from sql_db.database import session_local, Base, engine
from sql_db.models import Users
from sql_db.database import Base

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

@app.get("/get_api_key/")
def get_api_key(api_key: str = Header(), db: Session = Depends(get_db)) -> Optional[UserSchema]:

    user = db.query(Users).filter(Users.api_key == api_key).first()
    if user:
        return UserSchema(**user)
    else:
        return None