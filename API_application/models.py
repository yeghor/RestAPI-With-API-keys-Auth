from sqlalchemy import Column, Integer, String
from database import Base

class Users(Base):
    __tablename__ = "users"

    api_key = Column(String, primary_key=True, index=True)
    username = Column(String, index=True)
    date_joined = Column(String)
    requests = Column(Integer)