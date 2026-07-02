from sqlalchemy import Column, String, DateTime, Integer, Boolean
from sqlalchemy.sql import func
from app.database import Base


class Student(Base):
    """Student model for attendance tracking"""
    __tablename__ = "students"

    student_id = Column(Integer, primary_key=True, index=True)
    roll_number = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    department = Column(String(100), nullable=False)
    semester = Column(Integer, nullable=False)
    password_hash = Column(String(255), nullable=False)
    biometric_registered = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Student {self.roll_number}>"
