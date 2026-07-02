import json
import logging
from typing import List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings and configuration."""

    DATABASE_URL: Optional[str] = None
    MONGODB_URI: Optional[str] = None
    MONGODB_DB: str = "biometric_attendance"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    ADMIN_DEFAULT_USERNAME: str = "admin"
    ADMIN_DEFAULT_PASSWORD: Optional[str] = None

    ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    FRONTEND_URL: str = "http://localhost:5173"
    ORIGIN: Optional[str] = None

    RP_ID: str = "localhost"
    RP_NAME: str = "Biometric Attendance System"

    def get_origins(self) -> List[str]:
        raw = self.ORIGINS
        if isinstance(raw, str):
            raw = raw.strip()
            if not raw:
                return []
            if raw.startswith("[") and raw.endswith("]"):
                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    pass
            return [item.strip() for item in raw.split(",") if item.strip()]
        return list(raw)

    @field_validator("MONGODB_URI", mode="before")
    def normalize_mongodb_uri(cls, value, info):
        if value:
            return value
        if info.data.get("DATABASE_URL"):
            return info.data["DATABASE_URL"]
        raise ValueError("MONGODB_URI must be provided via environment variables.")

    @field_validator("SECRET_KEY", mode="before")
    def validate_secret_key(cls, value):
        if not value or not str(value).strip():
            raise ValueError("SECRET_KEY must be provided via environment variables.")
        return value

    @field_validator("ORIGIN", mode="before")
    def normalize_origin(cls, value, info):
        if value:
            return value
        if info.data.get("FRONTEND_URL"):
            return info.data["FRONTEND_URL"]
        return "http://localhost:5173"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
