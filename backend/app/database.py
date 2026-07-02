from pymongo import MongoClient
from pymongo.errors import PyMongoError
from app.config import settings

client = None
database = None


def get_client():
    """Create and cache the MongoDB client."""
    global client
    if client is None:
        client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
    return client


def get_database():
    """Get the configured MongoDB database."""
    global database
    if database is None:
        try:
            database = get_client()[settings.MONGODB_DB]
            ensure_indexes()
        except PyMongoError:
            database = get_client()[settings.MONGODB_DB]
    return database


def ensure_indexes():
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
    except PyMongoError:
        pass


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


def get_db():
    """Get the database dependency for FastAPI routes and services."""
    db = get_database()
    try:
        yield db
    finally:
        pass
