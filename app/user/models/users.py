from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from pydantic import EmailStr

class TokenResponse(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    username: str
    exp: Optional[int] = None
    refresh_tokens: list["RefreshToken"] = Relationship(back_populates="user")

class RefreshToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    token: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    is_revoked: bool = Field(default=False)
    
    user: Optional[User] = Relationship(back_populates="refresh_tokens")
