"""Logging utilities for the application."""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

import streamlit as st

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("nvidia-rag-chatbot")

def log_activity(username: str, activity: str, details: Optional[str] = None) -> None:
    """Log user activity.
    
    Args:
        username: Username of the user performing the activity.
        activity: Type of activity.
        details: Additional details about the activity.
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "username": username,
        "activity": activity,
        "details": details
    }
    
    # Add to session state for real-time tracking
    if "user_activity_log" not in st.session_state:
        st.session_state.user_activity_log = []
    
    st.session_state.user_activity_log.append(log_entry)
    
    # Log to file
    try:
        from src.utils.config import Config
        log_file = Config.USER_ACTIVITY_LOG_PATH
        
        existing_logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r') as file:
                existing_logs = json.load(file)
        
        existing_logs.append(log_entry)
        
        with open(log_file, 'w') as file:
            json.dump(existing_logs, file, indent=2)
    except Exception as e:
        logger.error(f"Error logging user activity: {str(e)}")
    
    # Log to Python logger
    logger.info(f"User activity: {username} - {activity} - {details}")

def get_activity_logs(limit: int = 100) -> list:
    """Get activity logs.
    
    Args:
        limit: Maximum number of logs to retrieve.
        
    Returns:
        list: List of activity logs.
    """
    try:
        from src.utils.config import Config
        log_file = Config.USER_ACTIVITY_LOG_PATH
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as file:
                logs = json.load(file)
            
            # Sort by timestamp in descending order
            logs.sort(key=lambda x: x["timestamp"], reverse=True)
            
            return logs[:limit]
    except Exception as e:
        logger.error(f"Error getting activity logs: {str(e)}")
    
    return []
