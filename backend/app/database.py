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
    """Create and cache the MongoDB client with improved resilience."""
    global client
    if client is None:
        try:
            # Try multiple connection strategies
            connection_kwargs = {
                "serverSelectionTimeoutMS": 20000,
                "connectTimeoutMS": 20000,
                "socketTimeoutMS": 20000,
                "retryWrites": True,
                "maxPoolSize": 10,
                "minPoolSize": 1,
            }
            
            # Strategy 1: Try with tlsAllowInvalidCertificates
            try:
                logger.info("Attempting MongoDB connection with tlsAllowInvalidCertificates...")
                client = MongoClient(
                    settings.MONGODB_URI,
                    **connection_kwargs,
                    ssl=True,
                    tlsAllowInvalidCertificates=True,
                )
                client.admin.command('ping')
                logger.info("MongoDB connection successful with tlsAllowInvalidCertificates")
                return client
            except Exception as e1:
                logger.warning(f"Strategy 1 failed: {e1}")
            
            # Strategy 2: Try with custom SSL context
            try:
                logger.info("Attempting MongoDB connection with custom SSL context...")
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
                client = MongoClient(
                    settings.MONGODB_URI,
                    **connection_kwargs,
                    ssl_context=ssl_context,
                )
                client.admin.command('ping')
                logger.info("MongoDB connection successful with custom SSL context")
                return client
            except Exception as e2:
                logger.warning(f"Strategy 2 failed: {e2}")
            
            # Strategy 3: Try without SSL verification
            try:
                logger.info("Attempting MongoDB connection without SSL certificate verification...")
                client = MongoClient(
                    settings.MONGODB_URI,
                    **connection_kwargs,
                    ssl=True,
                    tlsInsecure=True,
                )
                client.admin.command('ping')
                logger.info("MongoDB connection successful with tlsInsecure=True")
                return client
            except Exception as e3:
                logger.warning(f"Strategy 3 failed: {e3}")
            
            # Strategy 4: Last resort - try without any SSL options
            try:
                logger.info("Attempting MongoDB connection with default settings...")
                client = MongoClient(
                    settings.MONGODB_URI,
                    **connection_kwargs,
                )
                client.admin.command('ping')
                logger.info("MongoDB connection successful with default settings")
                return client
            except Exception as e4:
                logger.error(f"All MongoDB connection strategies failed")
                logger.error(f"Strategy 4 error: {e4}")
                raise
                
        except Exception as e:
            logger.error(f"Failed to establish MongoDB connection: {e}")
            raise
    
    return client


def get_database():
    """Get the configured MongoDB database with retry logic."""
    global database
    if database is None:
        try:
            client = get_client()
            database = client[settings.MONGODB_DB]
            logger.info(f"Successfully connected to database: {settings.MONGODB_DB}")
        except Exception as exc:
            logger.error(f"Failed to get MongoDB database: {exc}")
            raise
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
