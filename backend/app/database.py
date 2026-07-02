import logging
from typing import Generator, Optional
import ssl

from pymongo import MongoClient
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError
from app.config import settings

logger = logging.getLogger(__name__)
client: Optional[MongoClient] = None
database = None
_connection_error: Optional[Exception] = None


def get_client() -> Optional[MongoClient]:
    """Create and cache the MongoDB client with maximum resilience."""
    global client, _connection_error
    
    if client is not None:
        return client
    
    if _connection_error is not None:
        logger.warning(f"MongoDB previously failed to connect: {_connection_error}")
        # Try again in case connection is now available
    
    try:
        # Strategy 1: Try with tlsAllowInvalidCertificates
        logger.info("Attempting MongoDB connection (strategy 1)...")
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
        )
        client.admin.command('ping')
        logger.info("✓ MongoDB connected successfully (strategy 1)")
        _connection_error = None
        return client
    except Exception as e1:
        logger.warning(f"Strategy 1 failed: {type(e1).__name__}: {e1}")
    
    try:
        # Strategy 2: Try with custom SSL context
        logger.info("Attempting MongoDB connection (strategy 2)...")
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        client = MongoClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=20000,
            connectTimeoutMS=20000,
            socketTimeoutMS=20000,
            retryWrites=True,
            maxPoolSize=10,
            minPoolSize=1,
            ssl_context=ssl_context,
        )
        client.admin.command('ping')
        logger.info("✓ MongoDB connected successfully (strategy 2)")
        _connection_error = None
        return client
    except Exception as e2:
        logger.warning(f"Strategy 2 failed: {type(e2).__name__}: {e2}")
    
    try:
        # Strategy 3: Try with tlsInsecure
        logger.info("Attempting MongoDB connection (strategy 3)...")
        client = MongoClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=20000,
            connectTimeoutMS=20000,
            socketTimeoutMS=20000,
            retryWrites=True,
            maxPoolSize=10,
            minPoolSize=1,
            ssl=True,
            tlsInsecure=True,
        )
        client.admin.command('ping')
        logger.info("✓ MongoDB connected successfully (strategy 3)")
        _connection_error = None
        return client
    except Exception as e3:
        logger.warning(f"Strategy 3 failed: {type(e3).__name__}: {e3}")
    
    try:
        # Strategy 4: Try without any SSL options
        logger.info("Attempting MongoDB connection (strategy 4)...")
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
        logger.info("✓ MongoDB connected successfully (strategy 4)")
        _connection_error = None
        return client
    except Exception as e4:
        logger.warning(f"Strategy 4 failed: {type(e4).__name__}: {e4}")
        _connection_error = e4
    
    logger.error(f"All MongoDB connection strategies failed. Last error: {_connection_error}")
    # Return None instead of raising - let routes handle gracefully
    return None


def get_database():
    """Get the configured MongoDB database with maximum resilience."""
    global database
    if database is None:
        client = get_client()
        if client is None:
            logger.error("Cannot initialize database - MongoDB client unavailable")
            raise RuntimeError("MongoDB connection unavailable. Check logs for details.")
        
        try:
            database = client[settings.MONGODB_DB]
            logger.info(f"Successfully initialized database: {settings.MONGODB_DB}")
        except Exception as e:
            logger.error(f"Failed to get database object: {e}", exc_info=True)
            raise RuntimeError(f"Cannot access database: {e}")
    
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
