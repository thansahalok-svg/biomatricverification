import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
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
    logger.info("=" * 70)
    logger.info("APPLICATION STARTUP")
    logger.info("=" * 70)
    
    # CRITICAL: Verify MongoDB connection first
    logger.info("Step 1: Verifying MongoDB connection...")
    try:
        client = get_client()
        if client is None:
            raise RuntimeError("MongoDB client initialization returned None - check logs for connection details")
        
        # Verify the connection actually works
        client.admin.command("ping")
        logger.info("✓ MongoDB connection verified successfully")
    except Exception as exc:
        logger.error("=" * 70)
        logger.error("CRITICAL: MONGODB CONNECTION FAILED")
        logger.error("=" * 70)
        logger.error("The application cannot start without a working MongoDB connection.")
        logger.error(f"Error: {exc}")
        logger.error("=" * 70)
        logger.error("\nDebugging Steps:")
        logger.error("1. Check your MONGODB_URI environment variable is correct")
        logger.error("2. Verify MongoDB Atlas Network Access includes this server's IP")
        logger.error("3. Check MongoDB Atlas credentials (username/password)")
        logger.error("4. Verify the cluster is online and accessible")
        logger.error("5. Check DNS resolution for the cluster hostname")
        logger.error("=" * 70)
        raise RuntimeError(f"MongoDB connection failed: {exc}") from exc
    
    # CRITICAL: Create indexes and initialize default data
    logger.info("Step 2: Ensuring database indexes...")
    try:
        ensure_indexes()
        logger.info("✓ Database indexes ensured")
    except Exception as e:
        logger.error("Failed to create database indexes: %s", e)
        raise RuntimeError(f"Could not create indexes: {e}") from e
    
    # Initialize default admin user if it doesn't exist
    logger.info("Step 3: Initializing default admin user...")
    try:
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
            logger.info("✓ Default admin user created: %s", settings.ADMIN_DEFAULT_USERNAME)
        else:
            logger.info("✓ Admin user already exists")
    except PyMongoError as exc:
        logger.error("Failed to initialize admin user: %s", exc)
        raise RuntimeError(f"Could not initialize admin user: {exc}") from exc
    except Exception as exc:
        logger.error("Unexpected error during admin initialization: %s", exc)
        raise RuntimeError(f"Unexpected error during admin initialization: {exc}") from exc
    
    logger.info("=" * 70)
    logger.info("✓ APPLICATION STARTUP COMPLETE - ALL SYSTEMS OPERATIONAL")
    logger.info("=" * 70)

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


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to provide detailed error messages."""
    logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc),
            "type": type(exc).__name__,
            "path": str(request.url.path),
        }
    )


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
