from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.sql import func
from app.database import Base


class Admin(Base):
    """Admin model for system administrators"""
    __tablename__ = "admins"

    admin_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=True)
    full_name = Column(String(120), nullable=True)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Admin {self.username}>"
