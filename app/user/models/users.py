from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import EmailStr

class User(SQLModel, table=True):
    email: str = Field(default=None, primary_key=True)
    username: str
    exp: Optional[int]

class TokenResponse(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str
