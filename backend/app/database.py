import logging
from typing import Generator, Optional

from pymongo import MongoClient
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError
from app.config import settings

logger = logging.getLogger(__name__)
client: Optional[MongoClient] = None
database = None


def get_client() -> Optional[MongoClient]:
    """
    Create and cache the MongoDB client.
    
    Uses a single production-ready configuration for MongoDB Atlas.
    The connection string should be a valid MongoDB URI (mongodb+srv://... or mongodb://...).
    TLS is automatically enabled for mongodb+srv:// URIs by PyMongo.
    """
    global client
    
    if client is not None:
        return client
    
    try:
        logger.info("Connecting to MongoDB Atlas...")
        
        # Production-ready MongoDB connection configuration
        # MongoDB Atlas URIs (mongodb+srv://) automatically use TLS
        # No additional SSL parameters needed for valid certificates
        client = MongoClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=30000,
            socketTimeoutMS=30000,
            retryWrites=True,
            maxPoolSize=10,
            minPoolSize=1,
            # ConnectionPoolOptions for better stability on Render
            maxIdleTimeMS=45000,
        )
        
        # Verify connection is working
        client.admin.command('ping')
        logger.info("✓ MongoDB connection successful")
        
        return client
        
    except ServerSelectionTimeoutError as e:
        logger.error(f"MongoDB connection timeout. Check your MONGODB_URI and network connectivity: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {type(e).__name__}: {e}")
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
