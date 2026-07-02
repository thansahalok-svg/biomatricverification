from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Date, Time
from sqlalchemy.sql import func
from app.database import Base


class Attendance(Base):
    """Attendance record model"""
    __tablename__ = "attendance"

    attendance_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    check_in_time = Column(Time, nullable=False)
    status = Column(String(20), default="present")  # present, absent, late, leave
    verification_method = Column(String(50), default="webauthn")  # webauthn, manual
    device_information = Column(String(255), nullable=True)  # Browser, OS info
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Attendance {self.student_id} - {self.date}>"
