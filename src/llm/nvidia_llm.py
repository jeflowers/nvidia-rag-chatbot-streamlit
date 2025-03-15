"""NVIDIA LLM integration."""

from typing import Optional

from llama_index.core import Settings
from llama_index.embeddings.nvidia import NVIDIAEmbedding
from llama_index.llms.nvidia import NVIDIA

from src.utils.logger import logger
from src.utils.config import Config


def configure_llm_settings() -> None:
    """Configure LlamaIndex settings for NVIDIA LLM."""
    try:
        # Validate NVIDIA API key
        if not Config.NVIDIA_API_KEY:
            error_msg = "NVIDIA_API_KEY environment variable is not set."
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Configure settings
        from llama_index.core.node_parser import SentenceSplitter
        
        Settings.text_splitter = SentenceSplitter(chunk_size=500)
        Settings.embed_model = NVIDIAEmbedding(
            Config.EMBEDDING_MODEL,
            truncate="END"
        )
        Settings.llm = NVIDIA(model=Config.LLM_MODEL)
        
        logger.info("Successfully configured LLM settings.")
    except Exception as e:
        logger.error(f"Error configuring LLM settings: {str(e)}")
        raise


def get_embedding_model() -> Optional[NVIDIAEmbedding]:
    """Get the NVIDIA embedding model.
    
    Returns:
        Optional[NVIDIAEmbedding]: NVIDIA embedding model.
    """
    try:
        embed_model = NVIDIAEmbedding(
            Config.EMBEDDING_MODEL,
            truncate="END"
        )
        return embed_model
    except Exception as e:
        logger.error(f"Error initializing embedding model: {str(e)}")
        return None


def get_llm() -> Optional[NVIDIA]:
    """Get the NVIDIA LLM.
    
    Returns:
        Optional[NVIDIA]: NVIDIA LLM.
    """
    try:
        llm = NVIDIA(model=Config.LLM_MODEL)
        return llm
    except Exception as e:
        logger.error(f"Error initializing LLM: {str(e)}")
        return None
