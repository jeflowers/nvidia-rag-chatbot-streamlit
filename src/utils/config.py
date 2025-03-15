"""Configuration utilities for the application."""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration class."""
    
    # NVIDIA API settings
    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
    
    # Authentication settings
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin@123")
    SESSION_EXPIRY_MINUTES = int(os.getenv("SESSION_EXPIRY_MINUTES", "30"))
    MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
    IP_COOLDOWN_MINUTES = int(os.getenv("IP_COOLDOWN_MINUTES", "15"))
    
    # Database settings
    DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()
    SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "db/qnachat.db")
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    MONGODB_DB = os.getenv("MONGODB_DB", "qnachat")
    
    # File paths
    USER_CONFIG_PATH = "users.yaml"
    USER_ACTIVITY_LOG_PATH = "user_activity.json"
    
    # LLM settings
    EMBEDDING_MODEL = "NV-Embed-QA"
    LLM_MODEL = "meta/llama-3.1-405b-instruct"
    
    # Vector store settings
    VECTOR_STORE_PATH = "./milvus_demo.db"
    EMBEDDING_DIMENSION = 1024
    
    @classmethod
    def validate(cls) -> Optional[str]:
        """Validate configuration.
        
        Returns:
            Optional[str]: Error message if validation fails, None otherwise.
        """
        if not cls.NVIDIA_API_KEY:
            return "NVIDIA_API_KEY environment variable is not set."
        
        if cls.DB_TYPE not in ["sqlite", "mongodb"]:
            return f"Unsupported database type: {cls.DB_TYPE}"
        
        return None
    
    @classmethod
    def as_dict(cls) -> Dict[str, Any]:
        """Convert configuration to dictionary.
        
        Returns:
            Dict[str, Any]: Configuration dictionary.
        """
        return {
            "nvidia_api_key": cls.NVIDIA_API_KEY,
            "admin_username": cls.ADMIN_USERNAME,
            "session_expiry_minutes": cls.SESSION_EXPIRY_MINUTES,
            "max_login_attempts": cls.MAX_LOGIN_ATTEMPTS,
            "ip_cooldown_minutes": cls.IP_COOLDOWN_MINUTES,
            "db_type": cls.DB_TYPE,
            "sqlite_db_path": cls.SQLITE_DB_PATH,
            "mongodb_uri": cls.MONGODB_URI,
            "mongodb_db": cls.MONGODB_DB,
            "user_config_path": cls.USER_CONFIG_PATH,
            "user_activity_log_path": cls.USER_ACTIVITY_LOG_PATH,
            "embedding_model": cls.EMBEDDING_MODEL,
            "llm_model": cls.LLM_MODEL,
            "vector_store_path": cls.VECTOR_STORE_PATH,
            "embedding_dimension": cls.EMBEDDING_DIMENSION
        }
