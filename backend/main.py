from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.config import settings
from app.database import ensure_indexes, get_database
from app.routes import admin_auth, student_auth, webauthn, attendance, student, admin
from app.utils.security import hash_password

# Initialize MongoDB indexes
ensure_indexes()

# Create default admin user if none exists
try:
    db = get_database()
    existing_admin = db["admins"].find_one({})
    if not existing_admin:
        default_admin = {
            "admin_id": 1,
            "username": settings.ADMIN_DEFAULT_USERNAME,
            "password_hash": hash_password(settings.ADMIN_DEFAULT_PASSWORD),
            "email": None,
            "full_name": "System Administrator",
            "is_active": True,
        }
        db["admins"].insert_one(default_admin)
        print(f"Default admin user created: {settings.ADMIN_DEFAULT_USERNAME}")
except Exception:
    pass

# Initialize FastAPI app
app = FastAPI(
    title="Biometric Attendance System",
    description="WebAuthn-based attendance management system",
    version="1.0.0"
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "localhost:5173", "localhost:3000", "localhost:5000", "10.182.234.13", "10.182.234.13:5173", "10.182.234.13:5000"]
)

# Include routers
app.include_router(admin_auth.router)
app.include_router(student_auth.router)
app.include_router(webauthn.router)
app.include_router(attendance.router)
app.include_router(student.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Biometric Attendance System API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=True
    )
