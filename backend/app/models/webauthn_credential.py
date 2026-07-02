from sqlalchemy import Column, String, DateTime, Integer, LargeBinary, ForeignKey, JSON
from sqlalchemy.sql import func
from app.database import Base


class WebAuthnCredential(Base):
    """WebAuthn credential storage for FIDO2 authentication"""
    __tablename__ = "webauthn_credentials"

    credential_id = Column(String(255), primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False, index=True)
    public_key = Column(LargeBinary, nullable=False)
    sign_count = Column(Integer, default=0)
    transports = Column(JSON, nullable=True)  # List of transports (e.g., ["usb", "ble"])
    authenticator_type = Column(String(50), nullable=True)  # e.g., "platform", "cross-platform"
    registered_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<WebAuthnCredential {self.credential_id[:20]}...>"
