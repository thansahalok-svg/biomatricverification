from fastapi import APIRouter, Depends, HTTPException, status, Header
from app.database import get_database
from app.schemas.student import StudentResponse, StudentUpdate
from app.utils.security import decode_token
from typing import Optional
from datetime import datetime, timezone

router = APIRouter(prefix="/api/students", tags=["students"])


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


@router.get("/profile", response_model=StudentResponse)
async def get_profile(
    current_student: dict = Depends(get_current_student)
):
    """Get current student profile"""
    return current_student


@router.put("/profile", response_model=StudentResponse)
async def update_profile(
    update_data: StudentUpdate,
    current_student: dict = Depends(get_current_student)
):
    """Update current student profile"""

    db = get_database()
    update_fields = {}

    if update_data.full_name is not None:
        update_fields["full_name"] = update_data.full_name

    if update_data.phone is not None:
        update_fields["phone"] = update_data.phone

    if update_data.email is not None:
        existing = db["students"].find_one({
            "email": update_data.email,
            "student_id": {"$ne": current_student["student_id"]}
        })

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )

        update_fields["email"] = update_data.email

    if update_fields:
        update_fields["updated_at"] = datetime.now(timezone.utc)
        db["students"].update_one(
            {"student_id": current_student["student_id"]},
            {"$set": update_fields}
        )
        current_student.update(update_fields)

    return current_student
