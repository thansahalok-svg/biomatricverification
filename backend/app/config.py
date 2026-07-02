import json

from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings and configuration"""

    # Database
    DATABASE_URL: str = "mongodb+srv://josephdebbarma:eerDArfOfMV6Z8jp@biomatric.7baqjse.mongodb.net/biometric_attendance"
    MONGODB_URI: str = "mongodb+srv://josephdebbarma:eerDArfOfMV6Z8jp@biomatric.7baqjse.mongodb.net/biometric_attendance"
    MONGODB_DB: str = "biometric_attendance"

    # JWT
    SECRET_KEY: str = "4fcd4f09baf035834851e607b18a69bd"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Admin
    ADMIN_DEFAULT_USERNAME: str = "admin"
    ADMIN_DEFAULT_PASSWORD: str = "admin123"

    # CORS - Allow all origins for development
    ORIGINS: str = "*"

    # WebAuthn
    RP_ID: str = "localhost"
    RP_NAME: str = "Biometric Attendance System"
    ORIGIN: str = "http://localhost:5173"

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

    class Config:
        env_file = ".env"


settings = Settings()
