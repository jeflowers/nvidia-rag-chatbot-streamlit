"""Document processing utilities."""

from typing import List, Dict, Any, Optional

from llama_index.core import Document as LlamaDocument
from llama_index.core.node_parser import SentenceSplitter

from src.utils.logger import logger
from src.utils.config import Config


class DocumentProcessor:
    """Document processor class."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """Initialize the document processor.
        
        Args:
            chunk_size: Size of document chunks.
            chunk_overlap: Overlap between chunks.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    
    def process_documents(self, documents: List[LlamaDocument]) -> List[LlamaDocument]:
        """Process documents by chunking and metadata extraction.
        
        Args:
            documents: List of documents to process.
            
        Returns:
            List[LlamaDocument]: List of processed documents.
        """
        if not documents:
            logger.warning("No documents to process.")
            return []
        
        logger.info(f"Processing {len(documents)} documents.")
        processed_documents = []
        
        for doc in documents:
            try:
                # Add additional metadata if available
                if hasattr(doc, 'metadata') and doc.metadata:
                    pass  # Future enhancement: extract more metadata
                
                # Split document into chunks
                chunks = self.text_splitter.split_text(doc.text)
                
                # Create a new document for each chunk
                for i, chunk in enumerate(chunks):
                    chunk_metadata = doc.metadata.copy() if hasattr(doc, 'metadata') else {}
                    chunk_metadata['chunk_id'] = i
                    chunk_metadata['total_chunks'] = len(chunks)
                    
                    processed_doc = LlamaDocument(
                        text=chunk,
                        metadata=chunk_metadata
                    )
                    processed_documents.append(processed_doc)
                
                logger.debug(f"Processed document into {len(chunks)} chunks.")
            except Exception as e:
                logger.error(f"Error processing document: {str(e)}")
        
        logger.info(f"Processed documents into {len(processed_documents)} chunks.")
        return processed_documents
    
    def extract_metadata(self, document: LlamaDocument) -> Dict[str, Any]:
        """Extract metadata from a document.
        
        Args:
            document: Document to extract metadata from.
            
        Returns:
            Dict[str, Any]: Extracted metadata.
        """
        metadata = {}
        
        # Copy existing metadata
        if hasattr(document, 'metadata') and document.metadata:
            metadata.update(document.metadata)
        
        # Extract additional metadata (future enhancement)
        
        return metadata
