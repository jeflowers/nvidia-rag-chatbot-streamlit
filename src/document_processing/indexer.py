"""Document indexing utilities."""

from typing import List, Optional

import streamlit as st
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core import Document as LlamaDocument
from llama_index.vector_stores.milvus import MilvusVectorStore

from src.utils.logger import logger
from src.utils.config import Config
from src.vector_store.milvus import get_vector_store


class DocumentIndexer:
    """Document indexer class."""
    
    def __init__(self, vector_store: Optional[MilvusVectorStore] = None):
        """Initialize the document indexer.
        
        Args:
            vector_store: Vector store for document embeddings.
        """
        self.vector_store = vector_store or get_vector_store()
    
    def build_index(self, documents: List[LlamaDocument]) -> Optional[VectorStoreIndex]:
        """Build an index from documents.
        
        Args:
            documents: List of documents to index.
            
        Returns:
            Optional[VectorStoreIndex]: Vector index if successful, None otherwise.
        """
        if not documents:
            logger.warning("No documents to index.")
            return None
        
        try:
            logger.info(f"Building index for {len(documents)} documents.")
            
            # Create storage context with vector store
            storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
            
            # Build index
            index = VectorStoreIndex.from_documents(
                documents, 
                storage_context=storage_context
            )
            
            logger.info("Successfully built index.")
            return index
        except Exception as e:
            logger.error(f"Error building index: {str(e)}")
            return None
    
    def get_query_engine(self, index: Optional[VectorStoreIndex] = None, 
                         similarity_top_k: int = 20, streaming: bool = True):
        """Get a query engine for the index.
        
        Args:
            index: Vector index to query.
            similarity_top_k: Number of similar documents to retrieve.
            streaming: Whether to enable streaming responses.
            
        Returns:
            Query engine for the index.
        """
        if not index and "vector_index" in st.session_state:
            index = st.session_state.vector_index
        
        if not index:
            logger.warning("No index available for query engine.")
            return None
        
        try:
            logger.info("Creating query engine.")
            query_engine = index.as_query_engine(
                similarity_top_k=similarity_top_k,
                streaming=streaming
            )
            
            logger.info("Successfully created query engine.")
            return query_engine
        except Exception as e:
            logger.error(f"Error creating query engine: {str(e)}")
            return None
