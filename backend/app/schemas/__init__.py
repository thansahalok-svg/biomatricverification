from .admin import AdminCreate, AdminLogin, AdminResponse
from .student import StudentCreate, StudentUpdate, StudentResponse, StudentRegister
from .webauthn import (
    WebAuthnRegisterOptions,
    WebAuthnRegisterResponse,
    WebAuthnAuthenticateOptions,
    WebAuthnAuthenticateResponse
)
from .attendance import AttendanceCreate, AttendanceResponse
from .auth import Token, TokenPayload

__all__ = [
    "AdminCreate",
    "AdminLogin",
    "AdminResponse",
    "StudentCreate",
    "StudentUpdate",
    "StudentResponse",
    "StudentRegister",
    "WebAuthnRegisterOptions",
    "WebAuthnRegisterResponse",
    "WebAuthnAuthenticateOptions",
    "WebAuthnAuthenticateResponse",
    "AttendanceCreate",
    "AttendanceResponse",
    "Token",
    "TokenPayload"
]
