import logging
from typing import Generator, Optional
import ssl
import urllib.parse

from pymongo import MongoClient
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError
from app.config import settings

logger = logging.getLogger(__name__)
client: Optional[MongoClient] = None

database = None


def get_client() -> MongoClient:
    """Create and cache the MongoDB client."""
    global client
    if client is None:
        try:
            # Try with SSL but allow self-signed certificates
            client = MongoClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=20000,
                connectTimeoutMS=20000,
                socketTimeoutMS=20000,
                retryWrites=True,
                maxPoolSize=10,
                minPoolSize=1,
                ssl=True,
                tlsAllowInvalidCertificates=True,
                tlsInsecure=True,
            )
            # Test connection immediately
            client.admin.command('ping')
            logger.info("MongoDB connection successful")
        except Exception as e:
            logger.warning(f"MongoDB connection failed with standard SSL: {e}. Retrying without SSL verification...")
            # Fallback: Try with SSL disabled (for development/testing)
            try:
                # Parse URI to create connection without SSL if needed
                client = MongoClient(
                    settings.MONGODB_URI,
                    serverSelectionTimeoutMS=20000,
                    connectTimeoutMS=20000,
                    socketTimeoutMS=20000,
                    retryWrites=True,
                    maxPoolSize=10,
                    minPoolSize=1,
                )
                client.admin.command('ping')
                logger.info("MongoDB connection successful (fallback mode)")
            except Exception as e2:
                logger.error(f"MongoDB connection failed: {e2}")
                raise
    return client


def get_database():
    """Get the configured MongoDB database."""
    global database
    if database is None:
        try:
            client = get_client()
            database = client[settings.MONGODB_DB]
            ensure_indexes()
        except ServerSelectionTimeoutError as exc:
            logger.error("MongoDB unavailable during startup: %s", exc)
            raise
        except PyMongoError as exc:
            logger.warning("MongoDB warning while initializing: %s", exc)
            database = get_client()[settings.MONGODB_DB]
    return database


def ensure_indexes() -> None:
    """Create indexes for the main collections."""
    try:
        db = get_database()
        try:
            db["students"].create_index("email", unique=True)
            db["students"].create_index("roll_number", unique=True)
            db["students"].create_index("student_id", unique=True)
        except Exception as e:
            logger.warning("Could not create student indexes: %s", e)
        
        try:
            db["admins"].create_index("username", unique=True)
            db["admins"].create_index("email", unique=True)
        except Exception as e:
            logger.warning("Could not create admin indexes: %s", e)
        
        try:
            db["attendance"].create_index([("student_id", 1), ("date", 1)])
            db["attendance"].create_index("attendance_id", unique=True)
        except Exception as e:
            logger.warning("Could not create attendance indexes: %s", e)
        
        try:
            db["webauthn_credentials"].create_index("credential_id", unique=True)
            db["webauthn_credentials"].create_index("student_id")
        except Exception as e:
            logger.warning("Could not create webauthn indexes: %s", e)
        
        try:
            db["attendance_logs"].create_index([("student_id", 1), ("timestamp", -1)])
        except Exception as e:
            logger.warning("Could not create attendance_logs indexes: %s", e)
    except Exception as exc:
        logger.warning("Could not create MongoDB indexes: %s", exc)


def next_sequence(name: str) -> int:
    """Generate a monotonically increasing numeric ID."""
    counters = get_database()["counters"]
    result = counters.find_one_and_update(
        {"_id": name},
        {"$inc": {"value": 1}},
        upsert=True,
        return_document=True,
    )
    return result["value"]


def get_db() -> Generator:
    """Get the database dependency for FastAPI routes and services."""
    db = get_database()
    try:
        yield db
    finally:
        pass
