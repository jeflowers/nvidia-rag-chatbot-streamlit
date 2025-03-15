"""User model and operations."""

import yaml
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

import streamlit as st

from src.utils.config import Config
from src.utils.security import hash_password, verify_password
from src.utils.logger import log_activity
from src.database.base import DatabaseInterface


class User:
    """User model class."""
    
    def __init__(self, username: str, password_hash: str, is_admin: bool = False,
                 created_at: Optional[datetime] = None, last_login: Optional[datetime] = None):
        """Initialize a user.
        
        Args:
            username: Username of the user.
            password_hash: Hashed password of the user.
            is_admin: Whether the user is an admin.
            created_at: Timestamp when the user was created.
            last_login: Timestamp of the user's last login.
        """
        self.username = username
        self.password_hash = password_hash
        self.is_admin = is_admin
        self.created_at = created_at or datetime.now()
        self.last_login = last_login
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create a user from a dictionary.
        
        Args:
            data: Dictionary containing user data.
            
        Returns:
            User: User object.
        """
        created_at = None
        if data.get('created_at'):
            created_at = (
                datetime.fromisoformat(data['created_at'])
                if isinstance(data['created_at'], str)
                else data['created_at']
            )
        
        last_login = None
        if data.get('last_login'):
            last_login = (
                datetime.fromisoformat(data['last_login'])
                if isinstance(data['last_login'], str)
                else data['last_login']
            )
        
        return cls(
            username=data['username'],
            password_hash=data['password_hash'],
            is_admin=data.get('is_admin', False),
            created_at=created_at,
            last_login=last_login
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the user.
        """
        return {
            'username': self.username,
            'password_hash': self.password_hash,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def verify_password(self, password: str) -> bool:
        """Verify a password against the user's hash.
        
        Args:
            password: Password to verify.
            
        Returns:
            bool: True if password matches, False otherwise.
        """
        return verify_password(password, self.password_hash)
    
    def update_last_login(self) -> None:
        """Update the user's last login timestamp."""
        self.last_login = datetime.now()


class UserManager:
    """User management class."""
    
    def __init__(self, db: Optional[DatabaseInterface] = None):
        """Initialize the user manager.
        
        Args:
            db: Database interface for persistence.
        """
        self.db = db
        self._config_path = Config.USER_CONFIG_PATH
    
    def create_user(self, username: str, password: str, is_admin: bool = False) -> bool:
        """Create a new user.
        
        Args:
            username: Username of the user.
            password: Plain text password of the user.
            is_admin: Whether the user is an admin.
            
        Returns:
            bool: True if user was created, False if user already exists.
        """
        # Check if database interface is available
        if self.db:
            # Check if user already exists
            existing_user = self.db.get_user(username)
            if existing_user:
                return False
            
            # Store the new user
            return self.db.store_user(username, hash_password(password), is_admin)
        
        # Fall back to file-based storage
        config = self._load_config()
        
        if username in config.get("users", {}):
            return False
        
        if "users" not in config:
            config["users"] = {}
        
        config["users"][username] = {
            "username": username,
            "password_hash": hash_password(password),
            "is_admin": is_admin,
            "created_at": datetime.now().isoformat(),
            "last_login": None
        }
        
        self._save_config(config)
        return True
    
    def get_user(self, username: str) -> Optional[User]:
        """Get a user by username.
        
        Args:
            username: Username of the user.
            
        Returns:
            Optional[User]: User object if found, None otherwise.
        """
        # Check if database interface is available
        if self.db:
            user_data = self.db.get_user(username)
            if user_data:
                return User.from_dict(user_data)
            return None
        
        # Fall back to file-based storage
        config = self._load_config()
        
        if username not in config.get("users", {}):
            return None
        
        user_data = config["users"][username]
        user_data['username'] = username  # Ensure username is in the data
        return User.from_dict(user_data)
    
    def update_user_login(self, username: str) -> bool:
        """Update the last login timestamp for a user.
        
        Args:
            username: Username of the user.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        # Check if database interface is available
        if self.db:
            return self.db.update_user_login(username)
        
        # Fall back to file-based storage
        config = self._load_config()
        
        if username not in config.get("users", {}):
            return False
        
        config["users"][username]["last_login"] = datetime.now().isoformat()
        self._save_config(config)
        return True
    
    def delete_user(self, username: str) -> bool:
        """Delete a user.
        
        Args:
            username: Username of the user.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        # Check if database interface is available
        if self.db:
            return self.db.delete_user(username)
        
        # Fall back to file-based storage
        config = self._load_config()
        
        if username not in config.get("users", {}):
            return False
        
        del config["users"][username]
        self._save_config(config)
        return True
    
    def get_all_users(self) -> Dict[str, User]:
        """Get all users.
        
        Returns:
            Dict[str, User]: Dictionary mapping usernames to User objects.
        """
        # Check if database interface is available
        if self.db:
            users_data = self.db.get_all_users()
            return {
                username: User.from_dict(user_data)
                for username, user_data in users_data.items()
            }
        
        # Fall back to file-based storage
        config = self._load_config()
        
        return {
            username: User.from_dict({**user_data, 'username': username})
            for username, user_data in config.get("users", {}).items()
        }
    
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
