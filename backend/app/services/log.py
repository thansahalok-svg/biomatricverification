from datetime import datetime, timezone
from typing import Optional
from app.database import next_sequence


class LogService:
    """Service for logging authentication attempts and actions"""

    @staticmethod
    def log_action(
        student_id: Optional[int],
        action: str,
        success: bool,
        ip_address: Optional[str],
        user_agent: Optional[str],
        device_info: Optional[str],
        details: Optional[str],
        db
    ) -> dict:
        """Log an action"""

        log = {
            "log_id": next_sequence("log_id"),
            "student_id": student_id,
            "action": action,
            "success": success,
            "timestamp": datetime.now(timezone.utc),
            "ip_address": ip_address,
            "user_agent": user_agent,
            "device_info": device_info,
            "details": details,
        }

        db["attendance_logs"].insert_one(log)
        return log

    @staticmethod
    def get_logs(db, limit: int = 100):
        """Get recent logs"""

        return list(db["attendance_logs"].find().sort("timestamp", -1).limit(limit))
