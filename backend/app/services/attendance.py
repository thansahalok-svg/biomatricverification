from datetime import date, datetime, time, timezone
from fastapi import HTTPException, status
from app.database import next_sequence


class AttendanceService:
    """Service for handling attendance records"""

    @staticmethod
    def mark_attendance(
        student_id: int,
        check_in_time: time,
        device_info: str,
        db
    ) -> dict:
        """Mark attendance for a student"""

        student = db["students"].find_one({"student_id": student_id})
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )

        today = date.today()
        existing = db["attendance"].find_one({
            "student_id": student_id,
            "date": today
        })

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attendance already marked for today"
            )

        cutoff_time = time(9, 0, 0)
        status_val = "late" if check_in_time > cutoff_time else "present"
        now = datetime.now(timezone.utc)
        attendance = {
            "attendance_id": next_sequence("attendance_id"),
            "student_id": student_id,
            "date": today,
            "check_in_time": check_in_time,
            "status": status_val,
            "verification_method": "webauthn",
            "device_information": device_info,
            "created_at": now,
            "updated_at": now,
        }

        db["attendance"].insert_one(attendance)
        return attendance

    @staticmethod
    def get_student_attendance(student_id: int, db):
        """Get all attendance records for a student"""

        return list(db["attendance"].find({"student_id": student_id}).sort("date", -1))

    @staticmethod
    def get_attendance_percentage(student_id: int, db) -> dict:
        """Calculate attendance percentage for a student"""

        total = db["attendance"].count_documents({"student_id": student_id})
        present = db["attendance"].count_documents({
            "student_id": student_id,
            "status": {"$in": ["present", "late"]}
        })

        percentage = (present / total * 100) if total > 0 else 0

        return {
            "total_days": total,
            "present_days": present,
            "absent_days": total - present,
            "percentage": round(percentage, 2)
        }
