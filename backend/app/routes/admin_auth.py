from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_database
from app.schemas.admin import AdminCreate, AdminLogin, AdminResponse
from app.schemas.auth import Token
from app.utils.security import (
    hash_password,
    create_access_token,
    create_refresh_token
)
from app.services.auth import AuthService
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth/admin", tags=["admin-auth"])


@router.post("/register", response_model=AdminResponse)
async def register_admin(admin: AdminCreate):
    """Register a new admin account (only first admin, needs security)"""
    try:
        db = get_database()

        existing_admin = db["admins"].find_one({})
        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin registration is disabled. Contact system administrator."
            )

        password_hash = hash_password(admin.password)
        new_admin = {
            "admin_id": 1,
            "username": admin.username,
            "password_hash": password_hash,
            "email": admin.email,
            "full_name": admin.full_name,
            "is_active": True,
        }

        db["admins"].insert_one(new_admin)
        return new_admin
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin registration error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Admin registration failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login_admin(credentials: AdminLogin):
    """Admin login endpoint"""
    try:
        db = get_database()

        admin = AuthService.authenticate_admin(
            credentials.username,
            credentials.password,
            db
        )
        
        # Create tokens
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": str(admin["admin_id"]), "role": "admin"},
            expires_delta=access_token_expires
        )
        
        refresh_token = create_refresh_token(
            data={"sub": str(admin["admin_id"])},
            expires_delta=timedelta(days=7)
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1800
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )
        
