# NVIDIA RAG Q&A Chat Application - Implementation Guide

This guide provides detailed instructions for developers working on the NVIDIA RAG Q&A Chat Application.

## Development Environment Setup

### Prerequisites

- Python 3.8+
- NVIDIA API key
- Git

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/jeflowers/nvidia-rag-chatbot-streamlit.git
   cd nvidia-rag-chatbot-streamlit
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env file with your NVIDIA API key and other settings
   ```

5. Run the application:
   ```bash
   streamlit run app.py
   ```

## Project Structure

The application follows a modular architecture:

- `app.py`: Main entry point
- `src/`: Source code directory
  - `auth/`: Authentication module
  - `database/`: Database module
  - `document_processing/`: Document processing module
  - `llm/`: Language model module
  - `ui/`: User interface module
  - `utils/`: Utility functions
  - `vector_store/`: Vector database module
- `tests/`: Test suite
- `docs/`: Documentation
- `db/`: Database files

## Adding New Features

When adding new features:

1. Identify the appropriate module for your feature
2. Create necessary files following existing patterns
3. Update module's `__init__.py` to expose new functionality
4. Write tests for your feature
5. Document your feature in the appropriate guide

## Testing

Run tests with pytest:

```bash
python -m pytest
```

For coverage report:

```bash
python -m pytest --cov=src
```

## Database Management

The application supports two database backends:

- **SQLite**: Default for development and small-scale deployments
- **MongoDB**: Recommended for production deployments

Switch between them by setting `DB_TYPE` in your `.env` file.

## Deployment

See [README.md](../README.md) for deployment options and instructions.

## Troubleshooting

- Check logs in the console output
- Validate environment variables
- Ensure NVIDIA API key is valid and correctly set
- Verify database connection and configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write or update tests
5. Submit a pull request

Follow the code style and conventions established in the project.
