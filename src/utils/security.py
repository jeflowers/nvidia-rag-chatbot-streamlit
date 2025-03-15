"""Security utilities for the application."""

import hashlib
import secrets
import string
from typing import Tuple

def hash_password(password: str) -> str:
    """Hash a password using SHA-256.
    
    Args:
        password: Password to hash.
        
    Returns:
        str: Hashed password.
    """
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against a hash.
    
    Args:
        password: Password to verify.
        hashed_password: Hashed password to compare against.
        
    Returns:
        bool: True if password matches hash, False otherwise.
    """
    return hash_password(password) == hashed_password

def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token.
    
    Args:
        length: Length of the token.
        
    Returns:
        str: Secure random token.
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def sanitize_input(input_str: str) -> str:
    """Sanitize user input to prevent injection attacks.
    
    Args:
        input_str: Input string to sanitize.
        
    Returns:
        str: Sanitized input string.
    """
    # Remove potentially dangerous characters
    sanitized = input_str.replace("<", "&lt;").replace(">", "&gt;")
    return sanitized
