"""
Standalone MongoDB Atlas connection diagnostic script.

This script tests MongoDB connectivity without the full FastAPI application.
Use this to diagnose connection issues independently.

Usage:
    python test_mongodb_connection.py

Environment Variables Required:
    - MONGODB_URI: Full MongoDB Atlas connection string
    - MONGODB_DB: Database name (optional, defaults to 'biometric_attendance')
"""

import asyncio
import os
import sys
import logging
from typing import Optional
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


def diagnose_environment() -> None:
    """Diagnose Python environment and installed packages."""
    logger.info("=" * 70)
    logger.info("ENVIRONMENT DIAGNOSTICS")
    logger.info("=" * 70)
    
    # Python info
    logger.info(f"Python Version: {sys.version}")
    logger.info(f"Python Executable: {sys.executable}")
    
    # Check installed packages
    packages = {
        "pymongo": None,
        "motor": None,
        "dns (dnspython)": None,
        "certifi": None,
        "cryptography": None,
        "ssl": None,
    }
    
    try:
        import pymongo
        packages["pymongo"] = pymongo.__version__
    except Exception as e:
        packages["pymongo"] = f"ERROR: {e}"
    
    try:
        import motor
        packages["motor"] = motor.__version__
    except Exception as e:
        packages["motor"] = f"ERROR: {e}"
    
    try:
        import dns
        packages["dns (dnspython)"] = dns.__version__
    except Exception as e:
        packages["dns (dnspython)"] = f"ERROR: {e}"
    
    try:
        import certifi
        packages["certifi"] = certifi.__version__
    except Exception as e:
        packages["certifi"] = f"ERROR: {e}"
    
    try:
        import cryptography
        packages["cryptography"] = cryptography.__version__
    except Exception as e:
        packages["cryptography"] = f"ERROR: {e}"
    
    try:
        import ssl
        packages["ssl"] = ssl.OPENSSL_VERSION
    except Exception as e:
        packages["ssl"] = f"ERROR: {e}"
    
    for package, version in packages.items():
        logger.info(f"  {package}: {version}")
    
    logger.info("=" * 70)


def extract_cluster_info(uri: str) -> dict:
    """Extract and log cluster information from MongoDB URI without exposing credentials."""
    try:
        parsed = urlparse(uri)
        info = {
            "hostname": parsed.hostname,
            "scheme": parsed.scheme,
            "port": parsed.port,
            "username": "***" if parsed.username else None,
            "database": parsed.path.lstrip("/").split("?")[0] or "admin",
        }
        return info
    except Exception as e:
        logger.error(f"Could not parse MongoDB URI: {e}")
        return {}


async def test_pymongo_connection(mongodb_uri: str, mongodb_db: str) -> bool:
    """Test synchronous PyMongo connection (current implementation)."""
    logger.info("=" * 70)
    logger.info("TEST 1: PyMongo (Synchronous) Connection")
    logger.info("=" * 70)
    
    try:
        from pymongo import MongoClient
        from pymongo.errors import ServerSelectionTimeoutError
        
        logger.info(f"Creating PyMongo client with timeout=30000ms...")
        client = MongoClient(
            mongodb_uri,
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=30000,
            socketTimeoutMS=30000,
        )
        
        logger.info("Sending ping command...")
        client.admin.command("ping")
        logger.info("✓ PyMongo connection successful")
        logger.info(f"✓ Database '{mongodb_db}' accessible")
        client.close()
        return True
        
    except ServerSelectionTimeoutError as e:
        logger.error(f"✗ Connection timeout: {e}")
        logger.error("  Possible causes:")
        logger.error("    1. MongoDB Atlas IP whitelist doesn't include this server")
        logger.error("    2. DNS resolution failed for cluster")
        logger.error("    3. Network connection blocked by firewall")
        return False
        
    except Exception as e:
        logger.error(f"✗ PyMongo connection failed: {type(e).__name__}: {e}")
        return False


async def test_motor_connection(mongodb_uri: str, mongodb_db: str) -> bool:
    """Test asynchronous Motor connection (async implementation)."""
    logger.info("=" * 70)
    logger.info("TEST 2: Motor (Asynchronous) Connection")
    logger.info("=" * 70)
    
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        
        logger.info(f"Creating Motor AsyncIOMotorClient with timeout=30000ms...")
        client = AsyncIOMotorClient(
            mongodb_uri,
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=30000,
            socketTimeoutMS=30000,
        )
        
        logger.info("Sending ping command...")
        await client.admin.command("ping")
        logger.info("✓ Motor connection successful")
        logger.info(f"✓ Database '{mongodb_db}' accessible")
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"✗ Motor connection failed: {type(e).__name__}: {e}")
        
        # Provide specific guidance
        error_str = str(e).lower()
        if "ssl" in error_str or "tls" in error_str or "handshake" in error_str:
            logger.error("  TLS/SSL Issue detected:")
            logger.error("    - Verify MongoDB Atlas cluster has valid TLS certificates")
            logger.error("    - Check Python OpenSSL version is up-to-date")
            logger.error("    - Try standard mongodb:// URI instead of mongodb+srv://")
        elif "authentication" in error_str or "auth" in error_str:
            logger.error("  Authentication Issue detected:")
            logger.error("    - Verify username and password in MONGODB_URI")
            logger.error("    - Check user has appropriate roles in MongoDB Atlas")
        elif "dns" in error_str or "name" in error_str:
            logger.error("  DNS/Hostname Resolution Issue detected:")
            logger.error("    - Verify cluster hostname is correct")
            logger.error("    - Ensure dnspython is installed (for mongodb+srv://)")
            logger.error("    - Check /etc/hosts or DNS settings")
        
        return False


async def test_dns_resolution(mongodb_uri: str) -> bool:
    """Test DNS resolution for MongoDB cluster."""
    logger.info("=" * 70)
    logger.info("TEST 3: DNS Resolution")
    logger.info("=" * 70)
    
    try:
        import socket
        import asyncio
        
        cluster_info = extract_cluster_info(mongodb_uri)
        hostname = cluster_info.get("hostname")
        
        if not hostname:
            logger.warning("Could not extract hostname from URI")
            return False
        
        logger.info(f"Attempting to resolve: {hostname}")
        
        loop = asyncio.get_event_loop()
        ip_address = await loop.getaddrinfo(hostname, None)
        
        if ip_address:
            logger.info(f"✓ DNS resolution successful: {hostname}")
            for result in ip_address[:3]:  # Show first 3 results
                logger.info(f"  -> {result[4][0]}")
            return True
        else:
            logger.error(f"✗ DNS resolution failed: {hostname}")
            return False
            
    except Exception as e:
        logger.error(f"✗ DNS resolution error: {type(e).__name__}: {e}")
        logger.error("  Possible causes:")
        logger.error("    1. Hostname is incorrect")
        logger.error("    2. Network DNS service is unavailable")
        logger.error("    3. dnspython not installed (required for SRV records)")
        return False


async def main():
    """Run all connection tests."""
    logger.info("\n")
    logger.info("╔" + "=" * 68 + "╗")
    logger.info("║" + " " * 20 + "MongoDB Connection Diagnostic" + " " * 20 + "║")
    logger.info("╚" + "=" * 68 + "╝")
    logger.info("\n")
    
    # Get configuration from environment
    mongodb_uri = os.getenv("MONGODB_URI")
    mongodb_db = os.getenv("MONGODB_DB", "biometric_attendance")
    
    if not mongodb_uri:
        logger.error("ERROR: MONGODB_URI environment variable not set")
        logger.error("Usage: MONGODB_URI='mongodb+srv://...' python test_mongodb_connection.py")
        sys.exit(1)
    
    # Log cluster information
    logger.info("MONGODB CONFIGURATION")
    logger.info("=" * 70)
    cluster_info = extract_cluster_info(mongodb_uri)
    logger.info(f"  Cluster Hostname: {cluster_info.get('hostname')}")
    logger.info(f"  Connection Type: {cluster_info.get('scheme', 'unknown').upper()}")
    logger.info(f"  Database: {cluster_info.get('database', mongodb_db)}")
    logger.info(f"  Authenticated: {'Yes' if cluster_info.get('username') else 'No'}")
    logger.info("=" * 70)
    logger.info("\n")
    
    # Run diagnostics
    diagnose_environment()
    logger.info("\n")
    
    # Run connection tests
    dns_ok = await test_dns_resolution(mongodb_uri)
    logger.info("\n")
    
    pymongo_ok = await test_pymongo_connection(mongodb_uri, mongodb_db)
    logger.info("\n")
    
    motor_ok = await test_motor_connection(mongodb_uri, mongodb_db)
    logger.info("\n")
    
    # Summary
    logger.info("=" * 70)
    logger.info("TEST SUMMARY")
    logger.info("=" * 70)
    logger.info(f"DNS Resolution: {'✓ PASS' if dns_ok else '✗ FAIL'}")
    logger.info(f"PyMongo Connection: {'✓ PASS' if pymongo_ok else '✗ FAIL'}")
    logger.info(f"Motor Connection: {'✓ PASS' if motor_ok else '✗ FAIL'}")
    logger.info("=" * 70)
    logger.info("\n")
    
    # Provide final recommendation
    if motor_ok:
        logger.info("✓ All tests passed! MongoDB connection is working.")
        sys.exit(0)
    elif pymongo_ok and not motor_ok:
        logger.warning("⚠ PyMongo works but Motor fails. Check Motor installation.")
        sys.exit(1)
    else:
        logger.error("✗ MongoDB connection tests failed.")
        logger.error("See above for specific error details and troubleshooting steps.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
