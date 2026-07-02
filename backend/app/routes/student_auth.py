from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.student import StudentRegister, StudentResponse
from app.schemas.auth import Token, StudentLogin
from app.utils.security import create_access_token, create_refresh_token
from app.services.auth import AuthService
from datetime import timedelta

router = APIRouter(prefix="/api/auth/student", tags=["student-auth"])


@router.post("/register", response_model=StudentResponse)
async def register_student(student: StudentRegister, db: Session = Depends(get_db)):
    """Student registration endpoint"""
    
    new_student = AuthService.create_student(
        roll_number=student.roll_number,
        full_name=student.full_name,
        email=student.email,
        phone=student.phone,
        department=student.department,
        semester=student.semester,
        password=student.password,
        db=db
    )
    
    return new_student


@router.post("/login", response_model=Token)
async def login_student(
    credentials: StudentLogin,
    db: Session = Depends(get_db)
):
    """Student login endpoint"""
    
    # Authenticate student
    student = AuthService.authenticate_student(credentials.email, credentials.password, db)
    
    # Create tokens
    student_id = student.get("student_id") if isinstance(student, dict) else getattr(student, "student_id", None)
    if student_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to build login token for student"
        )

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(student_id), "role": "student"},
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        data={"sub": str(student_id), "role": "student"}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 30 * 60
    }
