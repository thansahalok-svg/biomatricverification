from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime


class StudentRegister(BaseModel):
    """Schema for student registration"""
    roll_number: str
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    department: str
    semester: int
    password: str
    
    @field_validator('password')
    def validate_password_length(cls, v):
        """Validate password doesn't exceed bcrypt 72-byte limit"""
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password must not exceed 72 bytes')
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v


class StudentCreate(BaseModel):
    """Schema for creating a student (admin)"""
    roll_number: str
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    department: str
    semester: int


class StudentUpdate(BaseModel):
    """Schema for updating student profile"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class StudentResponse(BaseModel):
    """Schema for student response"""
    student_id: int
    roll_number: str
    full_name: str
    email: str
    phone: Optional[str]
    department: str
    semester: int
    biometric_registered: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
