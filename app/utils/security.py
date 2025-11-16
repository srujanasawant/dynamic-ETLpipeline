# app/utils/security.py
import hashlib
import secrets
from typing import Optional
import structlog

logger = structlog.get_logger()


def hash_content(content: bytes) -> str:
    """Generate SHA256 hash of content"""
    return hashlib.sha256(content).hexdigest()


def generate_token(length: int = 32) -> str:
    """Generate secure random token"""
    return secrets.token_urlsafe(length)


def sanitize_query(query: str) -> str:
    """Basic SQL injection prevention"""
    # Remove comments
    query = query.replace('--', '')
    query = query.replace('/*', '')
    query = query.replace('*/', '')
    
    # Check for dangerous keywords
    dangerous = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'EXEC', 'EXECUTE']
    query_upper = query.upper()
    
    for keyword in dangerous:
        if keyword in query_upper:
            raise ValueError(f"Potentially dangerous SQL keyword detected: {keyword}")
    
    return query
