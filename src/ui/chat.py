"""Chat user interface."""

import time

import streamlit as st

from src.utils.logger import log_activity
from src.ui.sidebar import render_sidebar
from src.llm.query_engine import get_query_processor


def clear_chat() -> None:
    """Clear the chat history."""
    st.session_state.chat_history = []
    log_activity(st.session_state.current_user, "clear_chat")


def chat_ui() -> None:
    """Render the chat interface."""
    st.title("📚 RAG Q&A Chat Application")
    
    # Initialize chat history if not present
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Initialize documents loaded flag if not present
    if "documents_loaded" not in st.session_state:
        st.session_state.documents_loaded = False
    
    # Render sidebar and get uploaded files
    uploaded_files = render_sidebar()
    
    # Chat interface
    st.header("💬 Chat")
    
    # Display chat history
    for message, response in st.session_state.chat_history:
        st.chat_message("user").write(message)
        st.chat_message("assistant").write(response)
    
    # Display streaming response
    if "response_completed" in st.session_state and not st.session_state.response_completed:
        if "partial_response" in st.session_state and st.session_state.partial_response:
            st.chat_message("assistant").write(st.session_state.partial_response)
    
    # Input for new message
    if user_message := st.chat_input("Enter your question"):
        # Add user message to chat
        st.chat_message("user").write(user_message)
        
        if not st.session_state.documents_loaded:
            st.chat_message("assistant").write("Please load documents first.")
        else:
            # Process query
            query_processor = get_query_processor()
            
            def callback(response):
                """Callback function for when response is complete."""
                # Add to chat history
                st.session_state.chat_history.append((user_message, response))
            
            query_processor.process_query(user_message, callback)
            
            # Use a spinner while waiting for response
            with st.spinner("Generating response..."):
                while "response_completed" not in st.session_state or not st.session_state.response_completed:
                    st.experimental_rerun()
                    time.sleep(0.1)
            
            # Force rerun to update UI with new chat history
            st.experimental_rerun()
    
    # Clear chat button
    if st.button("Clear Chat"):
        clear_chat()
        st.experimental_rerun()
