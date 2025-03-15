"""Document loading utilities."""

import os
import tempfile
from typing import List, Optional, Tuple

import streamlit as st
from llama_index.core import SimpleDirectoryReader
from llama_index.core import Document as LlamaDocument

from src.utils.logger import log_activity, logger


class DocumentLoader:
    """Document loader class."""
    
    def __init__(self, temp_dir: Optional[str] = None):
        """Initialize the document loader.
        
        Args:
            temp_dir: Temporary directory for storing uploaded files.
        """
        self.temp_dir = temp_dir or tempfile.mkdtemp()
    
    def load_uploaded_files(self, uploaded_files: List) -> Tuple[List[str], List[LlamaDocument]]:
        """Load uploaded files.
        
        Args:
            uploaded_files: List of uploaded files from Streamlit.
            
        Returns:
            tuple: (List of file paths, List of loaded documents)
        """
        if not uploaded_files:
            logger.warning("No files uploaded.")
            return [], []
        
        file_paths = []
        
        # Save uploaded files to temporary directory
        for uploaded_file in uploaded_files:
            try:
                file_path = os.path.join(self.temp_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                file_paths.append(file_path)
                logger.info(f"Saved file: {uploaded_file.name}")
            except Exception as e:
                logger.error(f"Error saving file {uploaded_file.name}: {str(e)}")
        
        # Load documents
        documents = []
        for file_path in file_paths:
            try:
                file_documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
                documents.extend(file_documents)
                logger.info(f"Loaded document: {file_path}")
            except Exception as e:
                logger.error(f"Error loading document {file_path}: {str(e)}")
        
        if not documents:
            logger.warning("No documents loaded from uploaded files.")
        else:
            logger.info(f"Successfully loaded {len(documents)} documents from {len(file_paths)} files.")
        
        return file_paths, documents
    
    def load_from_directory(self, directory_path: str) -> List[LlamaDocument]:
        """Load documents from a directory.
        
        Args:
            directory_path: Path to the directory.
            
        Returns:
            List[LlamaDocument]: List of loaded documents.
        """
        try:
            documents = SimpleDirectoryReader(input_dir=directory_path).load_data()
            logger.info(f"Loaded {len(documents)} documents from directory: {directory_path}")
            return documents
        except Exception as e:
            logger.error(f"Error loading documents from directory {directory_path}: {str(e)}")
            return []
    
    def cleanup(self) -> None:
        """Clean up temporary files."""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
            logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            logger.error(f"Error cleaning up temporary directory {self.temp_dir}: {str(e)}")
