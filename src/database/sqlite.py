"""SQLite database implementation."""

import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

import streamlit as st

from src.utils.logger import logger
from src.utils.config import Config
from src.database.base import DatabaseInterface


class SQLiteDatabase(DatabaseInterface):
    """SQLite database implementation."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the SQLite database.
        
        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path or Config.SQLITE_DB_PATH
        self.conn = None
    
    def initialize(self) -> bool:
        """Initialize the database connection and create necessary tables.
        
        Returns:
            bool: True if initialization is successful, False otherwise.
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Connect to database
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            
            # Create users table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                is_admin BOOLEAN NOT NULL,
                created_at TEXT NOT NULL,
                last_login TEXT
            )
            ''')
            
            # Create sessions table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                FOREIGN KEY (username) REFERENCES users(username)
            )
            ''')
            
            # Create activity logs table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                username TEXT NOT NULL,
                activity TEXT NOT NULL,
                details TEXT,
                FOREIGN KEY (username) REFERENCES users(username)
            )
            ''')
            
            # Create chat history table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                session_id TEXT NOT NULL,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (username) REFERENCES users(username),
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
            ''')
            
            # Create documents table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                upload_timestamp TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                file_type TEXT NOT NULL,
                FOREIGN KEY (username) REFERENCES users(username)
            )
            ''')
            
            self.conn.commit()
            
            # Save connection to session state
            st.session_state.db_connection = self.conn
            
            logger.info(f"Initialized SQLite database at {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Error initializing SQLite database: {str(e)}")
            return False
    
    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("Closed SQLite database connection")
    
    def store_user(self, username: str, password_hash: str, is_admin: bool = False) -> bool:
        """Store user data in the database.
        
        Args:
            username: Username of the user.
            password_hash: Hashed password of the user.
            is_admin: Whether the user is an admin.
            
        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        try:
            created_at = datetime.now().isoformat()
            
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO users (username, password_hash, is_admin, created_at) VALUES (?, ?, ?, ?)",
                (username, password_hash, is_admin, created_at)
            )
            self.conn.commit()
            
            logger.info(f"Stored user: {username}")
            return True
        except Exception as e:
            logger.error(f"Error storing user {username}: {str(e)}")
            return False
    
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Retrieve user data from the database.
        
        Args:
            username: Username of the user.
            
        Returns:
            Optional[Dict[str, Any]]: User data if found, None otherwise.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT username, password_hash, is_admin, created_at, last_login FROM users WHERE username = ?",
                (username,)
            )
            user_data = cursor.fetchone()
            
            if user_data:
                return {
                    "username": user_data[0],
                    "password_hash": user_data[1],
                    "is_admin": bool(user_data[2]),
                    "created_at": user_data[3],
                    "last_login": user_data[4]
                }
            return None
        except Exception as e:
            logger.error(f"Error getting user {username}: {str(e)}")
            return None
    
    def update_user_login(self, username: str) -> bool:
        """Update the last login timestamp for a user.
        
        Args:
            username: Username of the user.
            
        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        try:
            last_login = datetime.now().isoformat()
            
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE users SET last_login = ? WHERE username = ?",
                (last_login, username)
            )
            self.conn.commit()
            
            logger.info(f"Updated last login for user: {username}")
            return True
        except Exception as e:
            logger.error(f"Error updating last login for user {username}: {str(e)}")
            return False
    
    def delete_user(self, username: str) -> bool:
        """Delete a user from the database.
        
        Args:
            username: Username of the user.
            
        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            self.conn.commit()
            
            logger.info(f"Deleted user: {username}")
            return True
        except Exception as e:
            logger.error(f"Error deleting user {username}: {str(e)}")
            return False
    
    def store_session(self, session_id: str, username: str, expires_at: datetime) -> bool:
        """Store session data in the database.
        
        Args:
            session_id: Unique identifier for the session.
            username: Username of the user.
            expires_at: Expiration timestamp for the session.
            
        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        try:
            created_at = datetime.now().isoformat()
            expires_at_iso = expires_at.isoformat()
            
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO sessions (session_id, username, created_at, expires_at) VALUES (?, ?, ?, ?)",
                (session_id, username, created_at, expires_at_iso)
            )
            self.conn.commit()
            
            logger.info(f"Stored session: {session_id} for user: {username}")
            return True
        except Exception as e:
            logger.error(f"Error storing session {session_id}: {str(e)}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session from the database.
        
        Args:
            session_id: Unique identifier for the session.
            
        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            self.conn.commit()
            
            logger.info(f"Deleted session: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {str(e)}")
            return False
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions from the database.
        
        Returns:
            int: Number of sessions removed.
        """
        try:
            current_time = datetime.now().isoformat()
            
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE expires_at < ?", (current_time,))
            deleted_count = cursor.rowcount
            self.conn.commit()
            
            logger.info(f"Cleaned up {deleted_count} expired sessions")
            return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {str(e)}")
            return 0
    
    def log_activity(self, username: str, activity: str, details: Optional[str] = None) -> bool:
        """Log user activity to the database.
        
        Args:
            username: Username of the user.
            activity: Type of activity.
            details: Additional details about the activity.
            
        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        try:
            timestamp = datetime.now().isoformat()
            
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO activity_logs (timestamp, username, activity, details) VALUES (?, ?, ?, ?)",
                (timestamp, username, activity, details)
            )
            self.conn.commit()
            
            logger.info(f"Logged activity: {username} - {activity}")
            return True
        except Exception as e:
            logger.error(f"Error logging activity: {str(e)}")
            return False
    
    def get_activity_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve activity logs from the database.
        
        Args:
            limit: Maximum number of logs to retrieve.
            
        Returns:
            List[Dict[str, Any]]: List of activity logs.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT timestamp, username, activity, details FROM activity_logs ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            logs = cursor.fetchall()
            
            return [
                {
                    "timestamp": log[0],
                    "username": log[1],
                    "activity": log[2],
                    "details": log[3]
                }
                for log in logs
            ]
        except Exception as e:
            logger.error(f"Error getting activity logs: {str(e)}")
            return []
    
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
        try:
            timestamp = datetime.now().isoformat()
            
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO chat_history (username, session_id, message, response, timestamp) VALUES (?, ?, ?, ?, ?)",
                (username, session_id, message, response, timestamp)
            )
            self.conn.commit()
            
            logger.info(f"Stored chat history for user: {username}")
            return True
        except Exception as e:
            logger.error(f"Error storing chat history: {str(e)}")
            return False
    
    def get_chat_history(self, username: str, session_id: Optional[str] = None) -> List[Tuple[str, str]]:
        """Retrieve chat history from the database.
        
        Args:
            username: Username of the user.
            session_id: Optional session ID to filter by.
            
        Returns:
            List[Tuple[str, str]]: List of (message, response) tuples.
        """
        try:
            cursor = self.conn.cursor()
            
            if session_id:
                cursor.execute(
                    "SELECT message, response FROM chat_history WHERE username = ? AND session_id = ? ORDER BY timestamp",
                    (username, session_id)
                )
            else:
                cursor.execute(
                    "SELECT message, response FROM chat_history WHERE username = ? ORDER BY timestamp",
                    (username,)
                )
                
            history = cursor.fetchall()
            return [(entry[0], entry[1]) for entry in history]
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            return []
    
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
        try:
            timestamp = datetime.now().isoformat()
            
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO documents (username, filename, file_path, upload_timestamp, file_size, file_type) VALUES (?, ?, ?, ?, ?, ?)",
                (username, filename, file_path, timestamp, file_size, file_type)
            )
            self.conn.commit()
            
            logger.info(f"Stored document metadata for file: {filename}")
            return True
        except Exception as e:
            logger.error(f"Error storing document metadata: {str(e)}")
            return False
    
    def get_user_documents(self, username: str) -> List[Dict[str, Any]]:
        """Retrieve document metadata for a user from the database.
        
        Args:
            username: Username of the user.
            
        Returns:
            List[Dict[str, Any]]: List of document metadata.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT filename, file_path, upload_timestamp, file_size, file_type FROM documents WHERE username = ? ORDER BY upload_timestamp DESC",
                (username,)
            )
            documents = cursor.fetchall()
            
            return [
                {
                    "filename": doc[0],
                    "file_path": doc[1],
                    "upload_timestamp": doc[2],
                    "file_size": doc[3],
                    "file_type": doc[4]
                }
                for doc in documents
            ]
        except Exception as e:
            logger.error(f"Error getting user documents: {str(e)}")
            return []
    
    def get_all_users(self) -> Dict[str, Dict[str, Any]]:
        """Retrieve all users from the database.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of username to user data.
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT username, password_hash, is_admin, created_at, last_login FROM users")
            users = cursor.fetchall()
            
            return {
                user[0]: {
                    "username": user[0],
                    "password_hash": user[1],
                    "is_admin": bool(user[2]),
                    "created_at": user[3],
                    "last_login": user[4]
                }
                for user in users
            }
        except Exception as e:
            logger.error(f"Error getting all users: {str(e)}")
            return {}
