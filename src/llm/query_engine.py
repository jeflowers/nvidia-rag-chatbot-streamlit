"""Query processing utilities."""

import time
from threading import Thread
from typing import Iterator, Optional, Callable

import streamlit as st

from src.utils.logger import logger
from src.utils.config import Config
from src.document_processing.indexer import DocumentIndexer


def stream_response(query_engine, message: str) -> Iterator[str]:
    """Stream a response from the query engine.
    
    Args:
        query_engine: Query engine to use.
        message: User message to respond to.
        
    Yields:
        str: Chunks of the response.
    """
    if query_engine is None:
        yield "Please load documents first."
        return
    
    try:
        response = query_engine.query(message)
        for text in response.response_gen:
            yield text
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        yield f"Error generating response: {str(e)}"


def process_query_in_thread(query_engine, message: str, callback: Optional[Callable] = None) -> None:
    """Process a query in a separate thread to allow for streaming responses.
    
    Args:
        query_engine: Query engine to use.
        message: User message to respond to.
        callback: Optional callback function to call when response is complete.
    """
    # Initialize or reset session state for streaming
    st.session_state.partial_response = ""
    st.session_state.response_completed = False
    
    def update_response():
        """Update the response in session state as it is generated."""
        full_response = ""
        try:
            for text in stream_response(query_engine, message):
                st.session_state.partial_response += text
                full_response += text
                time.sleep(0.01)  # Small delay to allow for UI updates
            
            # Store in database if available
            from src.auth.auth_manager import get_auth_manager
            auth_manager = get_auth_manager()
            if auth_manager.db and st.session_state.get("authenticated", False):
                auth_manager.db.store_chat_history(
                    st.session_state.current_user,
                    st.session_state.session_id,
                    message,
                    full_response
                )
            
            # Log activity
            if st.session_state.get("authenticated", False):
                from src.utils.logger import log_activity
                log_activity(
                    st.session_state.current_user,
                    "query",
                    f"Query: {message[:50]}..."
                )
        except Exception as e:
            logger.error(f"Error in query thread: {str(e)}")
        finally:
            st.session_state.response_completed = True
            if callback:
                callback(full_response)
    
    # Start thread for streaming response
    thread = Thread(target=update_response)
    thread.daemon = True  # Thread will die when main program exits
    thread.start()


class QueryProcessor:
    """Query processor class."""
    
    def __init__(self, query_engine=None):
        """Initialize the query processor.
        
        Args:
            query_engine: Query engine to use.
        """
        self.query_engine = query_engine
    
    def process_query(self, message: str, callback: Optional[Callable] = None) -> None:
        """Process a user query.
        
        Args:
            message: User message to respond to.
            callback: Optional callback function to call when response is complete.
        """
        if not self.query_engine:
            logger.warning("No query engine available.")
            st.session_state.partial_response = "Please load documents first."
            st.session_state.response_completed = True
            if callback:
                callback("Please load documents first.")
            return
        
        process_query_in_thread(self.query_engine, message, callback)
    
    def set_query_engine(self, query_engine) -> None:
        """Set the query engine.
        
        Args:
            query_engine: Query engine to use.
        """
        self.query_engine = query_engine


def get_query_processor() -> QueryProcessor:
    """Get the query processor singleton.
    
    Returns:
        QueryProcessor: Query processor instance.
    """
    if "query_processor" not in st.session_state:
        # Get query engine if available
        query_engine = None
        if "query_engine" in st.session_state:
            query_engine = st.session_state.query_engine
        
        st.session_state.query_processor = QueryProcessor(query_engine)
    
    return st.session_state.query_processor
