from fastapi import APIRouter, Depends, HTTPException, status, Header
from app.database import get_database
from app.utils.security import decode_token
from typing import Optional

router = APIRouter(prefix="/api/admin", tags=["admin"])


def get_current_admin(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = authorization.split(" ", 1)[1]
    token_data = decode_token(token)
    if not token_data or token_data.role != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    db = get_database()
    admin = db["admins"].find_one({"admin_id": int(token_data.sub)})
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")

    return admin


@router.get("/dashboard")
async def admin_dashboard(current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    students = list(db["students"].find({}, {"_id": 0, "password_hash": 0}).sort("student_id", 1))
    attendance = list(db["attendance"].find({}, {"_id": 0}).sort("date", -1))

    return {
        "admin": {
            "admin_id": current_admin["admin_id"],
            "username": current_admin["username"],
            "full_name": current_admin.get("full_name", "")
        },
        "students": students,
        "attendance": attendance,
        "summary": {
            "total_students": len(students),
            "total_attendance": len(attendance),
            "registered_biometrics": sum(1 for s in students if s.get("biometric_registered"))
        }
    }
