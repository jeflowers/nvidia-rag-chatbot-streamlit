"""Database module for the application."""

from typing import Optional

import streamlit as st

from src.utils.config import Config
from src.utils.logger import logger
from src.database.base import DatabaseInterface


def get_database() -> Optional[DatabaseInterface]:
    """Get the appropriate database interface based on configuration.
    
    Returns:
        Optional[DatabaseInterface]: Database interface if available, None otherwise.
    """
    # Check if database already exists in session state
    if "database" in st.session_state and st.session_state.database:
        return st.session_state.database
    
    db_type = Config.DB_TYPE.lower()
    db: Optional[DatabaseInterface] = None
    
    if db_type == "sqlite":
        from src.database.sqlite import SQLiteDatabase
        db = SQLiteDatabase(Config.SQLITE_DB_PATH)
    elif db_type == "mongodb":
        from src.database.mongodb import MongoDBDatabase
        db = MongoDBDatabase(Config.MONGODB_URI, Config.MONGODB_DB)
    else:
        logger.error(f"Unsupported database type: {db_type}")
        return None
    
    # Initialize database
    if db and db.initialize():
        # Save to session state
        st.session_state.database = db
        logger.info(f"Using {db_type} database")
        return db
    
    logger.error(f"Failed to initialize {db_type} database")
    return None


def close_database() -> None:
    """Close the database connection."""
    if "database" in st.session_state and st.session_state.database:
        st.session_state.database.close()
        del st.session_state.database
        logger.info("Closed database connection")
