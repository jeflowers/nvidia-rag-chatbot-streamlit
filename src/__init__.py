"""NVIDIA RAG Q&A Chat Application with Streamlit."""

import os
from importlib.metadata import version

__version__ = "0.1.0"

# Ensure required directories exist
os.makedirs("db", exist_ok=True)
