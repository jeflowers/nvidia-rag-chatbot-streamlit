"""Sidebar user interface components."""

from typing import List

import streamlit as st

from src.utils.logger import log_activity
from src.auth.auth_manager import logout_user
from src.document_processing.loader import DocumentLoader
from src.document_processing.processor import DocumentProcessor
from src.document_processing.indexer import DocumentIndexer


def render_sidebar() -> List:
    """Render the sidebar for the main application.
    
    Returns:
        List: List of uploaded files, if any.
    """
    with st.sidebar:
        st.write(f"Logged in as: **{st.session_state.current_user}**")
        
        # Logout button
        if st.button("Logout"):
            logout_user()
            st.experimental_rerun()
        
        # Admin panel button
        if st.session_state.admin_mode:
            if st.button("Admin Panel"):
                st.session_state.admin_view = True
                st.experimental_rerun()
        
        # Document upload
        st.header("📄 Document Upload")
        uploaded_files = st.file_uploader("Upload documents", accept_multiple_files=True)
        
        if st.button("Load Documents"):
            with st.spinner("Processing documents..."):
                # Load documents
                loader = DocumentLoader()
                file_paths, documents = loader.load_uploaded_files(uploaded_files)
                
                if not documents:
                    st.error("No documents found in the uploaded files.")
                    return uploaded_files
                
                # Process documents
                processor = DocumentProcessor()
                processed_docs = processor.process_documents(documents)
                
                # Create index
                indexer = DocumentIndexer()
                index = indexer.build_index(processed_docs)
                
                if not index:
                    st.error("Failed to build index from documents.")
                    return uploaded_files
                
                # Create query engine
                query_engine = indexer.get_query_engine(index)
                
                if not query_engine:
                    st.error("Failed to create query engine.")
                    return uploaded_files
                
                # Save to session state
                st.session_state.vector_index = index
                st.session_state.query_engine = query_engine
                st.session_state.documents_loaded = True
                
                # Update query processor
                from src.llm.query_engine import get_query_processor
                query_processor = get_query_processor()
                query_processor.set_query_engine(query_engine)
                
                # Log activity
                log_activity(
                    st.session_state.current_user,
                    "load_documents",
                    f"Loaded {len(uploaded_files)} documents"
                )
                
                st.success(f"Successfully loaded {len(documents)} documents from {len(file_paths)} files.")
        
        return uploaded_files
