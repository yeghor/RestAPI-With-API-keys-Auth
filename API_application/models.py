from sqlalchemy import Column, Integer, String, DateTime
from database import Base
from datetime import datetime
class Users(Base):
    __tablename__ = "users"

    api_key = Column(String, primary_key=True, index=True)
    username = Column(String, index=True)
    date_joined = Column(String)
    requests = Column(Integer)

class JWTs(Base):
    __tablename__ = "jwts"

    username = Column(String)
    jwt_token = Column(String, primary_key=True, index=True)
    issued_at = Column(DateTime, default=datetime.now())
    expires_at = Column(DateTime)