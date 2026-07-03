import logging
import sys
import ssl
from typing import Generator, Optional
from urllib.parse import urlparse

from pymongo import MongoClient, __version__ as pymongo_version
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError
from app.config import settings

logger = logging.getLogger(__name__)
client: Optional[MongoClient] = None
database = None

# Try to import Motor (async client) for future migrations
try:
    from motor.motor_asyncio import AsyncIOMotorClient
    MOTOR_AVAILABLE = True
except ImportError:
    MOTOR_AVAILABLE = False
    AsyncIOMotorClient = None


def log_environment_info() -> None:
    """Log diagnostic information about the Python and MongoDB environment."""
    try:
        import ssl as ssl_module
        import certifi
        
        logger.info("=" * 70)
        logger.info("ENVIRONMENT DIAGNOSTICS")
        logger.info("=" * 70)
        logger.info(f"Python Version: {sys.version}")
        logger.info(f"Python Executable: {sys.executable}")
        logger.info(f"PyMongo Version: {pymongo_version}")
        logger.info(f"OpenSSL Version: {ssl_module.OPENSSL_VERSION}")
        logger.info(f"SSL Default Cipher List Available: {bool(ssl_module.get_default_verify_paths())}")
        
        try:
            import dns
            logger.info(f"DNSPython Version: {dns.__version__}")
        except Exception as e:
            logger.warning(f"Could not determine DNSPython version: {e}")
        
        try:
            logger.info(f"Certifi CA Bundle: {certifi.where()}")
        except Exception as e:
            logger.warning(f"Could not determine Certifi CA bundle: {e}")
        
        logger.info("=" * 70)
    except Exception as e:
        logger.warning(f"Could not log environment info: {e}")


def extract_cluster_hostname(uri: str) -> Optional[str]:
    """Extract hostname from MongoDB URI without exposing credentials."""
    try:
        parsed = urlparse(uri)
        return parsed.hostname
    except Exception:
        return None


def get_client() -> Optional[MongoClient]:
    """
    Create and cache the MongoDB client with comprehensive error handling.
    
    Uses a single production-ready configuration for MongoDB Atlas.
    The connection string should be a valid MongoDB URI (mongodb+srv://... or mongodb://...).
    TLS is automatically enabled for mongodb+srv:// URIs by PyMongo.
    """
    global client
    
    if client is not None:
        return client
    
    try:
        # Log environment on first connection attempt
        log_environment_info()
        
        # Verify configuration
        if not settings.MONGODB_URI:
            error_msg = "MONGODB_URI environment variable is not set"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if not settings.MONGODB_DB:
            error_msg = "MONGODB_DB environment variable is not set"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Extract and log cluster info (without credentials)
        cluster_host = extract_cluster_hostname(settings.MONGODB_URI)
        logger.info(f"Connecting to MongoDB Atlas...")
        logger.info(f"  - Cluster: {cluster_host}")
        logger.info(f"  - Database: {settings.MONGODB_DB}")
        logger.info(f"  - Connection String Format: mongodb+srv://" + ("SRV" if "mongodb+srv" in settings.MONGODB_URI else "standard"))
        
        # Production-ready MongoDB connection configuration
        # MongoDB Atlas URIs (mongodb+srv://) automatically use TLS
        # PyMongo handles certificate validation by default
        logger.info("Creating MongoDB client...")
        
        client = MongoClient(
            settings.MONGODB_URI,
            # Connection timeouts optimized for Render
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=30000,
            socketTimeoutMS=30000,
            
            # Retry configuration for stability
            retryWrites=True,
            
            # Connection pooling optimized for Render's serverless environment
            maxPoolSize=10,
            minPoolSize=1,
            maxIdleTimeMS=45000,
        )
        
        # Verify connection is working
        logger.info("Attempting MongoDB ping command...")
        client.admin.command('ping')
        logger.info("✓ MongoDB connection successful - database is accessible")
        
        return client
        
    except ServerSelectionTimeoutError as e:
        logger.error("=" * 70)
        logger.error("MONGODB CONNECTION TIMEOUT")
        logger.error("=" * 70)
        logger.error(f"Failed to connect to MongoDB Atlas within 30 seconds")
        logger.error(f"Error Details: {e}")
        logger.error("")
        logger.error("TROUBLESHOOTING STEPS:")
        logger.error("1. MongoDB Atlas Network Access:")
        logger.error("   - Go to MongoDB Atlas Dashboard → Security → Network Access")
        logger.error("   - Add Render's IP range or use 0.0.0.0/0 (temporary for testing)")
        logger.error("   - If using Render, check their documentation for outbound IPs")
        logger.error("")
        logger.error("2. DNS Resolution:")
        logger.error("   - Run: python test_mongodb_connection.py")
        logger.error("   - Verify DNS can resolve cluster hostname")
        logger.error("   - Ensure dnspython is installed (in requirements.txt)")
        logger.error("")
        logger.error("3. MongoDB Atlas Cluster:")
        logger.error("   - Verify cluster is running (not paused)")
        logger.error("   - Check cluster status in MongoDB Atlas console")
        logger.error("")
        logger.error("4. Connection String:")
        logger.error(f"   - Cluster: {cluster_host}")
        logger.error(f"   - URI Format: {settings.MONGODB_URI[:20]}...***")
        logger.error(f"   - Ensure URI is correct and not modified in code")
        logger.error("=" * 70)
        return None
        
    except Exception as e:
        logger.error("=" * 70)
        logger.error("MONGODB CONNECTION ERROR")
        logger.error("=" * 70)
        logger.error(f"Error Type: {type(e).__name__}")
        logger.error(f"Error Message: {e}")
        logger.error("")
        
        # Provide specific guidance based on error type
        error_str = str(e).lower()
        
        if "ssl" in error_str or "tls" in error_str or "handshake" in error_str or "certificate" in error_str:
            logger.error("ROOT CAUSE: TLS/SSL Certificate Validation Issue")
            logger.error("")
            logger.error("SOLUTIONS:")
            logger.error("1. Update OpenSSL/Python:")
            logger.error("   - Render: OpenSSL is managed by Render's Python buildpack")
            logger.error("   - Local: pip install --upgrade cryptography certifi")
            logger.error("")
            logger.error("2. Check MongoDB Atlas Certificates:")
            logger.error("   - All MongoDB Atlas clusters use valid Let's Encrypt certs")
            logger.error("   - Issue usually indicates network proxy or firewall problem")
            logger.error("")
            logger.error("3. Try Connection String Variants:")
            logger.error("   - Current: mongodb+srv://... (uses SRV DNS records)")
            logger.error("   - Alternative: Use standard mongodb://... URI from Atlas")
            logger.error("")
            
        elif "authentication" in error_str or "auth" in error_str or "unauthorized" in error_str:
            logger.error("ROOT CAUSE: Authentication Failed")
            logger.error("")
            logger.error("TROUBLESHOOTING:")
            logger.error("1. Check MONGODB_URI Credentials:")
            logger.error("   - Verify username and password are correct")
            logger.error("   - URL-encode special characters (@, :, #, ?, etc.)")
            logger.error("")
            logger.error("2. MongoDB Atlas Database User:")
            logger.error("   - Go to MongoDB Atlas → Security → Database Access")
            logger.error("   - Verify user exists and has required roles")
            logger.error("   - User must have 'readWrite' role on database")
            logger.error("")
            logger.error("3. Check Database Name:")
            logger.error(f"   - Current database: {settings.MONGODB_DB}")
            logger.error("")
            
        elif "dns" in error_str or "name resolution" in error_str or "socket.gaierror" in error_str:
            logger.error("ROOT CAUSE: DNS Resolution Failed")
            logger.error("")
            logger.error("TROUBLESHOOTING:")
            logger.error("1. Verify dnspython Installation:")
            logger.error("   - Required for mongodb+srv:// URIs")
            logger.error("   - Check: pip list | grep dnspython")
            logger.error("   - Render: Should be installed from requirements.txt")
            logger.error("")
            logger.error("2. Test DNS Resolution:")
            logger.error("   - Run: python test_mongodb_connection.py")
            logger.error("   - Or: python -c \"import socket; socket.getaddrinfo('{hostname}', 27017)\"")
            logger.error("")
            logger.error("3. Check Cluster Hostname:")
            logger.error(f"   - Extracted hostname: {cluster_host}")
            logger.error("   - Must match MongoDB Atlas cluster name")
            logger.error("")
            
        elif "module not found" in error_str or "no module" in error_str:
            logger.error("ROOT CAUSE: Missing Required Package")
            logger.error("")
            logger.error("SOLUTION:")
            logger.error("- Install missing package: pip install -r requirements.txt")
            logger.error("- For Render: Ensure requirements.txt includes all packages")
            logger.error("- Run: python test_mongodb_connection.py to verify all packages")
            logger.error("")
            
        else:
            logger.error("UNKNOWN ERROR - Unable to determine root cause")
            logger.error("Run 'python test_mongodb_connection.py' for detailed diagnostics")
            logger.error("")
        
        logger.error(f"Cluster: {cluster_host}")
        logger.error(f"Database: {settings.MONGODB_DB}")
        logger.error("=" * 70)
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
