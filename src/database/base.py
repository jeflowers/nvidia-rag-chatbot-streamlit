"""Base database interface for the application."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple


class DatabaseInterface(ABC):
    """Abstract base class for database implementations."""
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the database connection and create necessary tables/collections.
        
        Returns:
            bool: True if initialization is successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close the database connection."""
        pass
    
    @abstractmethod
    def store_user(self, username: str, password_hash: str, is_admin: bool = False) -> bool:
        """Store user data in the database.
        
        Args:
            username: Username of the user.
            password_hash: Hashed password of the user.
            is_admin: Whether the user is an admin.
            
        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Retrieve user data from the database.
        
        Args:
            username: Username of the user.
            
        Returns:
            Optional[Dict[str, Any]]: User data if found, None otherwise.
        """
        pass
    
    @abstractmethod
    def update_user_login(self, username: str) -> bool:
        """Update the last login timestamp for a user.
        
        Args:
            username: Username of the user.
            
        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def delete_user(self, username: str) -> bool:
        """Delete a user from the database.
        
        Args:
            username: Username of the user.
            
        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def store_session(self, session_id: str, username: str, expires_at: datetime) -> bool:
        """Store session data in the database.
        
        Args:
            session_id: Unique identifier for the session.
            username: Username of the user.
            expires_at: Expiration timestamp for the session.
            
        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def delete_session(self, session_id: str) -> bool:
        """Delete a session from the database.
        
        Args:
            session_id: Unique identifier for the session.
            
        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions from the database.
        
        Returns:
            int: Number of sessions removed.
        """
        pass
    
    @abstractmethod
    def log_activity(self, username: str, activity: str, details: Optional[str] = None) -> bool:
        """Log user activity to the database.
        
        Args:
            username: Username of the user.
            activity: Type of activity.
            details: Additional details about the activity.
            
        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def get_activity_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve activity logs from the database.
        
        Args:
            limit: Maximum number of logs to retrieve.
            
        Returns:
            List[Dict[str, Any]]: List of activity logs.
        """
        pass
    
    @abstractmethod
    def store_chat_history(self, username: str, session_id: str, message: str, response: str) -> bool:
        """Store chat history in the database.
        
        Args:
            username: Username of the user.
            session_id: Unique identifier for the session.
            message: User's message.
            response: System's response.
            
        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def get_chat_history(self, username: str, session_id: Optional[str] = None) -> List[Tuple[str, str]]:
        """Retrieve chat history from the database.
        
        Args:
            username: Username of the user.
            session_id: Optional session ID to filter by.
            
        Returns:
            List[Tuple[str, str]]: List of (message, response) tuples.
        """
        pass
    
    @abstractmethod
    def store_document(self, username: str, filename: str, file_path: str, file_size: int, file_type: str) -> bool:
        """Store document metadata in the database.
        
        Args:
            username: Username of the user.
            filename: Name of the file.
            file_path: Path to the file.
            file_size: Size of the file in bytes.
            file_type: MIME type of the file.
            
        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def get_user_documents(self, username: str) -> List[Dict[str, Any]]:
        """Retrieve document metadata for a user from the database.
        
        Args:
            username: Username of the user.
            
        Returns:
            List[Dict[str, Any]]: List of document metadata.
        """
        pass
    
    @abstractmethod
    def get_all_users(self) -> Dict[str, Dict[str, Any]]:
        """Retrieve all users from the database.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of username to user data.
        """
        pass
