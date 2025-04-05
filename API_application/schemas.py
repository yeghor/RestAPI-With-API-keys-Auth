from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Annotated

class UserBase(BaseModel):
    username: str
    api_key: str

class UserSchema(UserBase):
    date_joined: Optional[str]
    requests: Optional[int]