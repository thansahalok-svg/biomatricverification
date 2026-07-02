from fastapi import APIRouter, Depends, HTTPException, status, Header
from app.database import get_database
from app.schemas.attendance import AttendanceResponse
from app.services.attendance import AttendanceService
from app.utils.security import decode_token
from datetime import datetime, time
from typing import Optional

router = APIRouter(prefix="/api/attendance", tags=["attendance"])


def get_current_student(authorization: Optional[str] = Header(None)) -> dict:
    """Dependency to get current authenticated student"""
    db = get_database()

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )

    token = parts[1]
    token_data = decode_token(token)

    if not token_data or token_data.role != "student":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    student = db["students"].find_one({"student_id": token_data.sub})
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    return student


@router.post("/mark", response_model=AttendanceResponse)
async def mark_attendance(
    device_info: str,
    current_student: dict = Depends(get_current_student)
):
    """Mark attendance for current student"""

    db = get_database()
    current_time = time(datetime.now().hour, datetime.now().minute, datetime.now().second)

    attendance = AttendanceService.mark_attendance(
        student_id=current_student["student_id"],
        check_in_time=current_time,
        device_info=device_info,
        db=db
    )

    return attendance


@router.get("/history")
async def get_attendance_history(
    current_student: dict = Depends(get_current_student)
):
    """Get attendance history for current student"""

    db = get_database()
    records = AttendanceService.get_student_attendance(current_student["student_id"], db)

    return {
        "student_id": current_student["student_id"],
        "attendance_records": [
            {
                "attendance_id": r["attendance_id"],
                "date": r["date"].isoformat() if hasattr(r["date"], "isoformat") else r["date"],
                "check_in_time": r["check_in_time"].isoformat() if hasattr(r["check_in_time"], "isoformat") else r["check_in_time"],
                "status": r["status"],
                "verification_method": r["verification_method"]
            }
            for r in records
        ]
    }


@router.get("/percentage")
async def get_attendance_percentage(
    current_student: dict = Depends(get_current_student)
):
    """Get attendance percentage for current student"""

    db = get_database()
    percentage = AttendanceService.get_attendance_percentage(
        current_student["student_id"],
        db
    )

    return percentage
