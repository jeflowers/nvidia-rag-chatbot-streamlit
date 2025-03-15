"""Session management for authentication."""

import os
import yaml
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

import streamlit as st

from src.utils.config import Config
from src.utils.logger import log_activity
from src.database.base import DatabaseInterface


class Session:
    """Session model class."""
    
    def __init__(self, session_id: str, username: str, created_at: datetime, expires_at: datetime):
        """Initialize a session.
        
        Args:
            session_id: Unique identifier for the session.
            username: Username of the user.
            created_at: Timestamp when the session was created.
            expires_at: Timestamp when the session will expire.
        """
        self.session_id = session_id
        self.username = username
        self.created_at = created_at
        self.expires_at = expires_at
    
    def is_expired(self) -> bool:
        """Check if the session is expired.
        
        Returns:
            bool: True if expired, False otherwise.
        """
        return datetime.now() > self.expires_at
    
    def extend(self, minutes: int = None) -> None:
        """Extend the session expiration time.
        
        Args:
            minutes: Number of minutes to extend by. Defaults to SESSION_EXPIRY_MINUTES.
        """
        if minutes is None:
            minutes = Config.SESSION_EXPIRY_MINUTES
        
        self.expires_at = datetime.now() + timedelta(minutes=minutes)


class SessionManager:
    """Session management class."""
    
    def __init__(self, db: Optional[DatabaseInterface] = None):
        """Initialize the session manager.
        
        Args:
            db: Database interface for persistence.
        """
        self.db = db
        self._config_path = Config.USER_CONFIG_PATH
    
    def create_session(self, username: str) -> Optional[Session]:
        """Create a new session for a user.
        
        Args:
            username: Username of the user.
            
        Returns:
            Optional[Session]: Created session or None if creation failed.
        """
        session_id = str(uuid.uuid4())
        created_at = datetime.now()
        expires_at = created_at + timedelta(minutes=Config.SESSION_EXPIRY_MINUTES)
        
        # Check if database interface is available
        if self.db:
            success = self.db.store_session(session_id, username, expires_at)
            if not success:
                return None
        else:
            # Fall back to file-based storage
            config = self._load_config()
            
            if "active_sessions" not in config:
                config["active_sessions"] = {}
            
            config["active_sessions"][session_id] = {
                "username": username,
                "created_at": created_at.isoformat(),
                "expires_at": expires_at.isoformat()
            }
            
            self._save_config(config)
        
        # Create session
        session = Session(
            session_id=session_id,
            username=username,
            created_at=created_at,
            expires_at=expires_at
        )
        
        # Update session state
        st.session_state.authenticated = True
        st.session_state.current_user = username
        st.session_state.session_id = session_id
        st.session_state.session_expiry = expires_at
        
        return session
    
    def validate_session(self, session_id: str) -> bool:
        """Validate a session.
        
        Args:
            session_id: Unique identifier for the session.
            
        Returns:
            bool: True if session is valid, False otherwise.
        """
        if not session_id:
            return False
        
        # Check current session state first
        if hasattr(st.session_state, 'session_id') and st.session_state.session_id == session_id:
            if hasattr(st.session_state, 'session_expiry'):
                if datetime.now() > st.session_state.session_expiry:
                    self.delete_session(session_id)
                    return False
                
                # Extend session
                new_expiry = datetime.now() + timedelta(minutes=Config.SESSION_EXPIRY_MINUTES)
                st.session_state.session_expiry = new_expiry
                
                # Update in database if available
                if self.db:
                    self.db.store_session(session_id, st.session_state.current_user, new_expiry)
                else:
                    # Fall back to file-based storage
                    config = self._load_config()
                    if "active_sessions" in config and session_id in config["active_sessions"]:
                        config["active_sessions"][session_id]["expires_at"] = new_expiry.isoformat()
                        self._save_config(config)
                
                return True
        
        # If not in session state or missing expiry, check database or file
        if self.db:
            # TODO: Implement database session validation
            pass
        else:
            # Fall back to file-based validation
            config = self._load_config()
            if "active_sessions" in config and session_id in config["active_sessions"]:
                session_data = config["active_sessions"][session_id]
                expires_at = datetime.fromisoformat(session_data["expires_at"])
                
                if datetime.now() > expires_at:
                    self.delete_session(session_id)
                    return False
                
                # Extend session
                new_expiry = datetime.now() + timedelta(minutes=Config.SESSION_EXPIRY_MINUTES)
                config["active_sessions"][session_id]["expires_at"] = new_expiry.isoformat()
                self._save_config(config)
                
                # Update session state
                st.session_state.session_expiry = new_expiry
                
                return True
        
        return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session.
        
        Args:
            session_id: Unique identifier for the session.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        # Check if database interface is available
        if self.db:
            return self.db.delete_session(session_id)
        
        # Fall back to file-based storage
        config = self._load_config()
        
        if "active_sessions" in config and session_id in config["active_sessions"]:
            del config["active_sessions"][session_id]
            self._save_config(config)
            return True
        
        return False
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions.
        
        Returns:
            int: Number of sessions removed.
        """
        # Check if database interface is available
        if self.db:
            return self.db.cleanup_expired_sessions()
        
        # Fall back to file-based storage
        config = self._load_config()
        
        if "active_sessions" not in config:
            return 0
        
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session_data in config["active_sessions"].items():
            expires_at = datetime.fromisoformat(session_data["expires_at"])
            if current_time > expires_at:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del config["active_sessions"][session_id]
        
        if expired_sessions:
            self._save_config(config)
        
        return len(expired_sessions)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load user configuration from YAML file.
        
        Returns:
            Dict[str, Any]: Configuration dictionary.
        """
        try:
            if os.path.exists(self._config_path):
                with open(self._config_path, 'r') as file:
                    return yaml.safe_load(file) or {}
            return {"users": {}, "active_sessions": {}}
        except Exception as e:
            st.error(f"Error loading user configuration: {str(e)}")
            return {"users": {}, "active_sessions": {}}
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save user configuration to YAML file.
        
        Args:
            config: Configuration dictionary.
        """
        try:
            with open(self._config_path, 'w') as file:
                yaml.dump(config, file)
        except Exception as e:
            st.error(f"Error saving user configuration: {str(e)}")
