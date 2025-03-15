"""Milvus vector store integration."""

import os
from typing import Optional

import streamlit as st
from llama_index.vector_stores.milvus import MilvusVectorStore

from src.utils.logger import logger
from src.utils.config import Config


def get_vector_store() -> MilvusVectorStore:
    """Get a Milvus vector store instance.
    
    Returns:
        MilvusVectorStore: Milvus vector store instance.
    """
    # Check if vector store already exists in session state
    if "vector_store" in st.session_state and st.session_state.vector_store:
        return st.session_state.vector_store
    
    # Create new vector store
    try:
        vector_store = MilvusVectorStore(
            uri=Config.VECTOR_STORE_PATH,
            dim=Config.EMBEDDING_DIMENSION,
            overwrite=True
        )
        
        # Save to session state
        st.session_state.vector_store = vector_store
        
        logger.info(f"Created Milvus vector store at {Config.VECTOR_STORE_PATH}")
        return vector_store
    except Exception as e:
        logger.error(f"Error creating Milvus vector store: {str(e)}")
        st.error(f"Error creating Milvus vector store: {str(e)}")
        raise
