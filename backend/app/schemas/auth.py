from pydantic import BaseModel, EmailStr
from typing import Optional


class StudentLogin(BaseModel):
    """Schema for student login"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT Token response"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    """JWT Token payload"""
    sub: int  # User ID
    role: str  # "admin" or "student"
    exp: int  # Expiration time
