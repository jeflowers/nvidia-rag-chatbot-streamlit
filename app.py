"""NVIDIA RAG Q&A Chat Application - Streamlit Entry Point."""

import os
import atexit
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="RAG Q&A Chat Application",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if not present
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'documents_loaded' not in st.session_state:
    st.session_state.documents_loaded = False

if 'vector_store' not in st.session_state:
    st.session_state.vector_store = None

if 'query_engine' not in st.session_state:
    st.session_state.query_engine = None

if 'partial_response' not in st.session_state:
    st.session_state.partial_response = ""

if 'response_completed' not in st.session_state:
    st.session_state.response_completed = True
    
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'current_user' not in st.session_state:
    st.session_state.current_user = None
    
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
    
if 'session_expiry' not in st.session_state:
    st.session_state.session_expiry = None
    
if 'login_attempts' not in st.session_state:
    st.session_state.login_attempts = 0
    
if 'lockout_until' not in st.session_state:
    st.session_state.lockout_until = None
    
if 'admin_mode' not in st.session_state:
    st.session_state.admin_mode = False
    
if 'admin_view' not in st.session_state:
    st.session_state.admin_view = False

# Import application modules
from src.utils.config import Config
from src.utils.logger import logger
from src.ui.login import login_ui
from src.ui.admin_panel import admin_ui
from src.ui.chat import chat_ui
from src.auth.auth_manager import initialize_admin_account, validate_session
from src.llm.nvidia_llm import configure_llm_settings
from src.database import get_database, close_database


def main():
    """Main entry point for the application."""
    # Get database interface
    db = get_database()
    
    # Register cleanup function
    atexit.register(close_database)
    
    # Validate configuration
    error = Config.validate()
    if error:
        st.error(error)
        st.stop()
    
    # Configure LLM settings
    try:
        configure_llm_settings()
    except Exception as e:
        st.error(f"Error configuring LLM settings: {str(e)}")
        st.stop()
    
    # Initialize admin account if needed
    initialize_admin_account()
    
    # Check authentication
    if not st.session_state.authenticated:
        login_ui()
        return
    
    # Validate session
    if not validate_session():
        st.warning("Your session has expired. Please log in again.")
        login_ui()
        return
    
    # Determine which UI to display
    if st.session_state.admin_mode and st.session_state.admin_view:
        admin_ui()
    else:
        chat_ui()


if __name__ == "__main__":
    main()
