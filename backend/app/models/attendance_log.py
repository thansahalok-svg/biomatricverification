from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.database import Base


class AttendanceLog(Base):
    """Log for all authentication attempts and actions"""
    __tablename__ = "attendance_logs"

    log_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=True, index=True)
    action = Column(String(50), nullable=False)  # login, logout, biometric_register, attendance_mark, etc.
    success = Column(Boolean, default=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)  # Browser info
    device_info = Column(String(255), nullable=True)
    details = Column(String(500), nullable=True)

    def __repr__(self):
        return f"<AttendanceLog {self.action} - {self.timestamp}>"
