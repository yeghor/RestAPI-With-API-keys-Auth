from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Annotated

class UserSchema(BaseModel):
    username: str
    api_key: str
    date_joined: str
    requests: int