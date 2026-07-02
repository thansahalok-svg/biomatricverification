from datetime import datetime, timezone
from fastapi import HTTPException, status
from app.database import next_sequence
from app.utils.security import verify_password, hash_password


class AuthService:
    """Authentication service for handling login and user verification"""

    @staticmethod
    def authenticate_student(email: str, password: str, db) -> dict:
        """Authenticate student with email and password"""
        student = db["students"].find_one({"email": email})

        if not student or not student.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        if not verify_password(password, student.get("password_hash", "")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        return student

    @staticmethod
    def authenticate_admin(username: str, password: str, db) -> dict:
        """Authenticate admin with username and password"""
        admin = db["admins"].find_one({"username": username})

        if not admin or not admin.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        if not verify_password(password, admin.get("password_hash", "")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        return admin

    @staticmethod
    def create_student(
        roll_number: str,
        full_name: str,
        email: str,
        phone: str,
        department: str,
        semester: int,
        password: str,
        db
    ) -> dict:
        """Create a new student account"""

        existing = db["students"].find_one({
            "$or": [{"email": email}, {"roll_number": roll_number}]
        })

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student with this email or roll number already exists"
            )

        password_hash = hash_password(password)
        now = datetime.now(timezone.utc)
        student = {
            "student_id": next_sequence("student_id"),
            "roll_number": roll_number,
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "department": department,
            "semester": semester,
            "password_hash": password_hash,
            "biometric_registered": False,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }

        db["students"].insert_one(student)
        return student
