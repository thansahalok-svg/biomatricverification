from pydantic import BaseModel
from datetime import datetime, date, time
from typing import Optional


class AttendanceCreate(BaseModel):
    """Schema for creating attendance record"""
    student_id: int
    date: date
    check_in_time: time
    status: str = "present"
    verification_method: str = "webauthn"
    device_information: Optional[str] = None


class AttendanceResponse(BaseModel):
    """Schema for attendance response"""
    attendance_id: int
    student_id: int
    date: date
    check_in_time: time
    status: str
    verification_method: str
    device_information: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
