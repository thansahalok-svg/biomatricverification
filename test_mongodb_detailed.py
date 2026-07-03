"""
Detailed MongoDB Atlas connection diagnostic with TLS inspection.

This script performs deep inspection of the TLS handshake and MongoDB connection.
Use this to diagnose SSL handshake failures on Render.

Usage:
    MONGODB_URI="mongodb+srv://..." python test_mongodb_detailed.py
"""

import asyncio
import os
import sys
import logging
import socket
import ssl
from typing import Optional
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


def diagnose_tls_environment() -> None:
    """Diagnose TLS/SSL environment."""
    logger.info("=" * 70)
    logger.info("TLS/SSL ENVIRONMENT DIAGNOSTICS")
    logger.info("=" * 70)
    
    try:
        import ssl
        import certifi
        import OpenSSL
        import cryptography
        
        logger.info(f"Python Version: {sys.version}")
        logger.info(f"OpenSSL Version (ssl module): {ssl.OPENSSL_VERSION}")
        logger.info(f"PyOpenSSL Version: {OpenSSL.__version__}")
        logger.info(f"Cryptography Version: {cryptography.__version__}")
        logger.info(f"Certifi Version: {certifi.__version__}")
        logger.info(f"Certifi CA Bundle: {certifi.where()}")
        logger.info("")
        
        # Check SSL context defaults
        ctx = ssl.create_default_context()
        logger.info(f"Default TLS Version: {ctx.minimum_version}")
        logger.info(f"Check Hostname: {ctx.check_hostname}")
        logger.info(f"Verify Mode: {ctx.verify_mode}")
        logger.info(f"CA Certs Loaded: {ctx.ca_certs is not None}")
        logger.info("")
        
        # List available ciphers (just count, don't enumerate all)
        logger.info(f"Available Ciphers: {len(ctx.get_ciphers())}")
        logger.info("")
        
    except Exception as e:
        logger.error(f"Error diagnosing TLS: {e}", exc_info=True)
    
    logger.info("=" * 70)


def diagnose_pymongo_versions() -> None:
    """Check PyMongo and Motor versions."""
    logger.info("=" * 70)
    logger.info("PYMONGO/MOTOR VERSIONS")
    logger.info("=" * 70)
    
    try:
        import pymongo
        logger.info(f"PyMongo Version: {pymongo.__version__}")
    except Exception as e:
        logger.error(f"PyMongo: {e}")
    
    try:
        import motor
        logger.info(f"Motor Version: {motor.__version__}")
    except Exception as e:
        logger.error(f"Motor: {e}")
    
    try:
        import dns
        logger.info(f"DNSPython Version: {dns.__version__}")
    except Exception as e:
        logger.error(f"DNSPython: {e}")
    
    logger.info("=" * 70)


def extract_cluster_info(uri: str) -> dict:
    """Extract cluster information from MongoDB URI."""
    try:
        parsed = urlparse(uri)
        return {
            "scheme": parsed.scheme,
            "hostname": parsed.hostname,
            "port": parsed.port,
            "username": "***" if parsed.username else None,
            "password": "***" if parsed.password else None,
            "database": parsed.path.lstrip("/").split("?")[0] or "admin",
            "has_auth": bool(parsed.username),
        }
    except Exception as e:
        logger.error(f"Could not parse URI: {e}")
        return {}


async def test_dns_resolution(hostname: str) -> bool:
    """Test DNS SRV resolution."""
    logger.info("=" * 70)
    logger.info("TEST 1: DNS Resolution")
    logger.info("=" * 70)
    
    try:
        logger.info(f"Attempting DNS lookup for: {hostname}")
        loop = asyncio.get_event_loop()
        
        # Standard A/AAAA record lookup
        logger.info("  Standard DNS lookup (A/AAAA records)...")
        results = await loop.getaddrinfo(hostname, 27017, socket.AF_INET)
        if results:
            logger.info(f"  ✓ DNS resolution successful")
            for result in results[:3]:
                logger.info(f"    -> {result[4][0]}:{result[4][1]}")
            return True
        else:
            logger.error(f"  ✗ No DNS results for {hostname}")
            return False
            
    except Exception as e:
        logger.error(f"✗ DNS resolution failed: {type(e).__name__}: {e}")
        return False


async def test_socket_connection(hostname: str, port: int = 27017) -> bool:
    """Test raw socket connection without TLS."""
    logger.info("=" * 70)
    logger.info("TEST 2: Raw Socket Connection (No TLS)")
    logger.info("=" * 70)
    
    try:
        logger.info(f"Attempting socket connection to {hostname}:{port}")
        logger.info("  Creating socket...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        logger.info("  Connecting...")
        sock.connect((hostname, port))
        logger.info(f"  ✓ Socket connection successful")
        
        # Try to read the MongoDB handshake
        logger.info("  Waiting for MongoDB handshake...")
        data = sock.recv(1024)
        logger.info(f"  ✓ Received {len(data)} bytes from MongoDB")
        sock.close()
        return True
        
    except socket.timeout:
        logger.error(f"✗ Socket connection timeout")
        return False
    except Exception as e:
        logger.error(f"✗ Socket connection failed: {type(e).__name__}: {e}")
        return False


async def test_tls_handshake(hostname: str, port: int = 27017) -> bool:
    """Test TLS handshake."""
    logger.info("=" * 70)
    logger.info("TEST 3: TLS Handshake")
    logger.info("=" * 70)
    
    try:
        logger.info(f"Attempting TLS handshake with {hostname}:{port}")
        
        # Create default SSL context
        logger.info("  Creating SSL context...")
        context = ssl.create_default_context()
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        
        logger.info(f"  SSL context created (verify_mode={context.verify_mode})")
        logger.info(f"  Attempting TLS connection...")
        
        # Create socket and wrap with TLS
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        try:
            sock.connect((hostname, port))
            logger.info("  ✓ Socket connected, initiating TLS...")
            
            ssl_sock = context.wrap_socket(sock, server_hostname=hostname)
            logger.info("  ✓ TLS handshake successful")
            
            # Check certificate
            cert = ssl_sock.getpeercert()
            logger.info(f"  Certificate Subject: {cert.get('subject', 'N/A')}")
            logger.info(f"  Certificate Issuer: {cert.get('issuer', 'N/A')}")
            logger.info(f"  Protocol: {ssl_sock.version()}")
            logger.info(f"  Cipher: {ssl_sock.cipher()}")
            
            ssl_sock.close()
            return True
            
        except ssl.SSLError as e:
            logger.error(f"  ✗ TLS handshake failed: {type(e).__name__}: {e}")
            logger.error(f"    Error code: {e.errno}")
            logger.error(f"    SSL errno: {e.library}")
            return False
        finally:
            sock.close()
            
    except Exception as e:
        logger.error(f"✗ TLS test error: {type(e).__name__}: {e}")
        return False


async def test_pymongo_connection(mongodb_uri: str) -> bool:
    """Test PyMongo connection."""
    logger.info("=" * 70)
    logger.info("TEST 4: PyMongo Connection")
    logger.info("=" * 70)
    
    try:
        from pymongo import MongoClient
        from pymongo.errors import ServerSelectionTimeoutError, OperationFailure
        
        logger.info("Creating PyMongo client...")
        client = MongoClient(
            mongodb_uri,
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=30000,
            socketTimeoutMS=30000,
        )
        
        logger.info("Attempting ping...")
        client.admin.command("ping")
        logger.info("✓ PyMongo connection successful")
        client.close()
        return True
        
    except ServerSelectionTimeoutError as e:
        logger.error(f"✗ PyMongo timeout: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ PyMongo error: {type(e).__name__}: {e}")
        return False


async def main():
    """Run all diagnostic tests."""
    logger.info("\n")
    logger.info("╔" + "=" * 68 + "╗")
    logger.info("║" + " " * 15 + "MongoDB TLS Connection Diagnostic" + " " * 20 + "║")
    logger.info("╚" + "=" * 68 + "╝")
    logger.info("\n")
    
    # Get configuration
    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        logger.error("ERROR: MONGODB_URI environment variable not set")
        sys.exit(1)
    
    # Run diagnostics
    diagnose_tls_environment()
    logger.info("")
    diagnose_pymongo_versions()
    logger.info("")
    
    # Extract cluster info
    cluster_info = extract_cluster_info(mongodb_uri)
    logger.info("=" * 70)
    logger.info("MONGODB CONFIGURATION")
    logger.info("=" * 70)
    logger.info(f"Cluster: {cluster_info.get('hostname')}")
    logger.info(f"Scheme: {cluster_info.get('scheme')}")
    logger.info(f"Port: {cluster_info.get('port', 27017)}")
    logger.info(f"Database: {cluster_info.get('database')}")
    logger.info(f"Authenticated: {cluster_info.get('has_auth')}")
    logger.info("=" * 70)
    logger.info("\n")
    
    # Run tests
    hostname = cluster_info.get('hostname')
    if not hostname:
        logger.error("Could not extract hostname from URI")
        sys.exit(1)
    
    dns_ok = await test_dns_resolution(hostname)
    logger.info("")
    
    socket_ok = await test_socket_connection(hostname) if dns_ok else False
    logger.info("")
    
    tls_ok = await test_tls_handshake(hostname) if socket_ok else False
    logger.info("")
    
    pymongo_ok = await test_pymongo_connection(mongodb_uri)
    logger.info("")
    
    # Summary
    logger.info("=" * 70)
    logger.info("DIAGNOSTIC SUMMARY")
    logger.info("=" * 70)
    logger.info(f"DNS Resolution: {'✓ PASS' if dns_ok else '✗ FAIL'}")
    logger.info(f"Socket Connection: {'✓ PASS' if socket_ok else '✗ FAIL'}")
    logger.info(f"TLS Handshake: {'✓ PASS' if tls_ok else '✗ FAIL'}")
    logger.info(f"PyMongo Connection: {'✓ PASS' if pymongo_ok else '✗ FAIL'}")
    logger.info("=" * 70)
    logger.info("")
    
    if pymongo_ok:
        logger.info("✓ All tests passed! MongoDB connection is working.")
        sys.exit(0)
    else:
        logger.error("✗ MongoDB connection tests failed.")
        
        if not dns_ok:
            logger.error("  Problem: DNS resolution failed")
            logger.error("  Solution: Check cluster hostname and dnspython installation")
        elif not socket_ok:
            logger.error("  Problem: Cannot connect to MongoDB port 27017")
            logger.error("  Solution: Check MongoDB Atlas Network Access settings")
        elif not tls_ok:
            logger.error("  Problem: TLS handshake failed")
            logger.error("  Solution: Check OpenSSL compatibility or try different TLS settings")
        elif not pymongo_ok:
            logger.error("  Problem: PyMongo connection failed")
            logger.error("  Solution: Check credentials and database access")
        
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
