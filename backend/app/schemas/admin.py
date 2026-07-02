from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class AdminCreate(BaseModel):
    """Schema for creating an admin"""
    username: str
    password: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


class AdminLogin(BaseModel):
    """Schema for admin login"""
    username: str
    password: str


class AdminResponse(BaseModel):
    """Schema for admin response"""
    admin_id: int
    username: str
    email: Optional[str]
    full_name: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
