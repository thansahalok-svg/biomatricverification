import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from pymongo.errors import PyMongoError

from app.config import settings
from app.database import ensure_indexes, get_database, get_client
from app.routes import admin_auth, student_auth, webauthn, attendance, student, admin
from app.utils.security import hash_password

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Biometric Attendance System",
    description="WebAuthn-based attendance management system",
    version="1.0.0",
)

@app.on_event("startup")
async def startup_event() -> None:
    """Initialize MongoDB and default data on startup."""
    try:
        ensure_indexes()
        db = get_database()
        existing_admin = db["admins"].find_one({})
        if not existing_admin:
            default_password = settings.ADMIN_DEFAULT_PASSWORD or "admin123"
            default_admin = {
                "admin_id": 1,
                "username": settings.ADMIN_DEFAULT_USERNAME,
                "password_hash": hash_password(default_password),
                "email": None,
                "full_name": "System Administrator",
                "is_active": True,
            }
            db["admins"].insert_one(default_admin)
            logger.info("Default admin user created: %s", settings.ADMIN_DEFAULT_USERNAME)
    except PyMongoError as exc:
        logger.error("Failed MongoDB startup initialization: %s", exc)
    except Exception as exc:
        logger.error("Unexpected startup failure: %s", exc)

    finally:
        try:
            client = get_client()
            client.admin.command("ping")
        except Exception as exc:
            logger.warning("MongoDB ping failed during startup: %s", exc)

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
    allowed_hosts=["*"]
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
    """Health check endpoint."""
    return {
        "status": "ok"
    }


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=False,
        log_level="info",
    )
