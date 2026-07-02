import logging
from typing import Generator, Optional
import ssl

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
        # Create custom SSL context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        client = MongoClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=15000,
            connectTimeoutMS=15000,
            socketTimeoutMS=15000,
            ssl=True,
            ssl_context=ssl_context,
            retryWrites=True,
            maxPoolSize=10,
            minPoolSize=2,
        )
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
        db["students"].create_index("email", unique=True)
        db["students"].create_index("roll_number", unique=True)
        db["students"].create_index("student_id", unique=True)
        db["admins"].create_index("username", unique=True)
        db["admins"].create_index("email", unique=True)
        db["attendance"].create_index([("student_id", 1), ("date", 1)])
        db["attendance"].create_index("attendance_id", unique=True)
        db["webauthn_credentials"].create_index("credential_id", unique=True)
        db["webauthn_credentials"].create_index("student_id")
        db["attendance_logs"].create_index([("student_id", 1), ("timestamp", -1)])
    except PyMongoError as exc:
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
