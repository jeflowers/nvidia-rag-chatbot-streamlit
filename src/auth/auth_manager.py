"""Authentication manager for the application."""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple

import streamlit as st

from src.utils.config import Config
from src.utils.logger import log_activity
from src.auth.user import UserManager, User
from src.auth.session import SessionManager, Session
from src.database.base import DatabaseInterface


class AuthManager:
    """Authentication manager class."""
    
    def __init__(self, db: Optional[DatabaseInterface] = None):
        """Initialize the authentication manager.
        
        Args:
            db: Database interface for persistence.
        """
        self.db = db
        self.user_manager = UserManager(db)
        self.session_manager = SessionManager(db)
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate a user.
        
        Args:
            username: Username of the user.
            password: Password of the user.
            
        Returns:
            bool: True if authentication is successful, False otherwise.
        """
        # Get user
        user = self.user_manager.get_user(username)
        if not user or not user.verify_password(password):
            return False
        
        # Update last login time
        self.user_manager.update_user_login(username)
        
        # Create new session
        session = self.session_manager.create_session(username)
        if not session:
            return False
        
        # Set admin mode
        st.session_state.admin_mode = user.is_admin
        
        # Log activity
        log_activity(username, "login")
        
        return True
    
    def validate_session(self) -> bool:
        """Validate the current session.
        
        Returns:
            bool: True if session is valid, False otherwise.
        """
        if not st.session_state.get("authenticated", False) or not st.session_state.get("session_id"):
            return False
        
        return self.session_manager.validate_session(st.session_state.session_id)
    
    def logout_user(self) -> None:
        """Log out the current user."""
        if st.session_state.get("authenticated", False) and st.session_state.get("current_user"):
            log_activity(st.session_state.current_user, "logout")
        
        # Clear session 
        if st.session_state.get("session_id"):
            self.session_manager.delete_session(st.session_state.session_id)
        
        # Reset session state
        st.session_state.authenticated = False
        st.session_state.current_user = None
        st.session_state.session_id = None
        st.session_state.session_expiry = None
        st.session_state.admin_mode = False


# Initialize the authentication manager as a singleton
def get_auth_manager(db: Optional[DatabaseInterface] = None) -> AuthManager:
    """Get the authentication manager singleton.
    
    Args:
        db: Database interface for persistence.
        
    Returns:
        AuthManager: Authentication manager instance.
    """
    if "auth_manager" not in st.session_state:
        st.session_state.auth_manager = AuthManager(db)
    
    return st.session_state.auth_manager


def initialize_admin_account() -> None:
    """Initialize the admin account if it doesn't exist."""
    auth_manager = get_auth_manager()
    admin_username = Config.ADMIN_USERNAME
    admin_password = Config.ADMIN_PASSWORD
    
    # Check if any users exist
    users = auth_manager.user_manager.get_all_users()
    if not users:
        if auth_manager.user_manager.create_user(admin_username, admin_password, is_admin=True):
            st.success(f"Initial admin account created. Username: {admin_username}")


def validate_session() -> bool:
    """Validate the current session.
    
    Returns:
        bool: True if session is valid, False otherwise.
    """
    auth_manager = get_auth_manager()
    return auth_manager.validate_session()


def authenticate_user(username: str, password: str) -> bool:
    """Authenticate a user.
    
    Args:
        username: Username of the user.
        password: Password of the user.
        
    Returns:
        bool: True if authentication is successful, False otherwise.
    """
    auth_manager = get_auth_manager()
    return auth_manager.authenticate_user(username, password)


def logout_user() -> None:
    """Log out the current user."""
    auth_manager = get_auth_manager()
    auth_manager.logout_user()
