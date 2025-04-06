from pydantic import BaseModel, Field
from typing import Optional

class UserBase(BaseModel):
    username: str
    api_key: str = Field(title="Security API key. Need to access personal JWT work token")

class UserSchema(UserBase):
    date_joined: str = Field(title="User join to system date")
    requests: int = Field(default=0, title="Amount of user requests")

class JWTTokenReturn(BaseModel):
    detail: str = Field(title="Additional response details")
    authorization_token: str = Field(title="Personal auth token")
    issued_at: str = Field(title="Datestamp of token assigning")
    expires_at: str = Field(title="Token Expiring date")
