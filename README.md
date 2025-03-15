# NVIDIA RAG Q&A Chat Application - Streamlit Version

A modern document-based question answering application using NVIDIA AI technologies and LlamaIndex, with a Streamlit interface.

## Features

1. **Embedding Creation**: Utilizes NVIDIA NIM microservices to transform text into high-quality embeddings.
2. **Vector Database**: Employs GPU-accelerated Milvus for efficient storage and retrieval of embeddings.
3. **Inference with Llama3**: Leverages the NIM API's Llama3 model to handle user queries and generate accurate responses.
4. **Orchestration with LlamaIndex**: Integrates and manages all components seamlessly with LlamaIndex for a smooth Q&A experience.
5. **Streamlit Interface**: Provides a clean, modern web interface built with Streamlit.
6. **Secure Authentication**: Implements user authentication with password hashing and session management.
7. **Role-Based Access Control**: Supports admin and regular user roles with different permissions.
8. **Activity Logging**: Tracks user actions for security auditing and monitoring.
9. **Brute Force Protection**: Limits login attempts with automatic account lockouts.
10. **Database Integration**: Supports both SQLite (default) and MongoDB for data persistence.
11. **Document Tracking**: Maintains records of uploaded documents and their metadata.
12. **Chat History**: Preserves conversation history across sessions.

## Prerequisites

- Python 3.8+
- NVIDIA API Key (set as an environment variable `NVIDIA_API_KEY`)

### Getting an NVIDIA API Key

To use this application, you'll need an NVIDIA API key. Follow these steps to obtain one:

1. Visit the NVIDIA AI Foundation Models page: [https://build.nvidia.com/explore/discover](https://build.nvidia.com/explore/discover)
2. If you don't have an NVIDIA account, click on "Sign Up" to create one.
3. Once logged in, navigate to the API section or look for an option to generate an API key.
4. Follow the prompts to create a new API key. You may need to agree to terms of service and select the services you plan to use.
5. Once generated, copy your API key and keep it secure.
6. Set the API key as an environment variable on your system:
   - On Unix-based systems (Linux, macOS):
     ```
     export NVIDIA_API_KEY='your_api_key_here'
     ```
   - On Windows (Command Prompt):
     ```
     set NVIDIA_API_KEY=your_api_key_here
     ```
   - On Windows (PowerShell):
     ```
     $env:NVIDIA_API_KEY='your_api_key_here'
     ```

## Installation

### Standard Installation

1. Clone this repository:
   ```
   git clone https://github.com/jeflowers/nvidia-rag-chatbot-streamlit.git
   cd nvidia-rag-chatbot-streamlit
   ```

2. Install the requirements:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on the example:
   ```
   cp .env.example .env
   ```
   
4. Edit the `.env` file to add your NVIDIA API key and customize other settings.

5. Run the application:
   ```
   streamlit run app.py
   ```

### Development Installation

If you plan to modify the code or contribute to the project, install it in development mode:

```
pip install -e .
```

## Usage

1. Run the application:
   ```
   streamlit run app.py
   ```

2. Your web browser should automatically open to the application (usually at `http://localhost:8501`).

3. Log in with the default admin credentials (unless changed in your `.env` file):
   - Username: `admin`
   - Password: `admin@123`

4. Use the interface to:
   - Upload documents via the sidebar
   - Load the documents into the system
   - Ask questions based on the loaded documents

## Docker Deployment

You can also run the application using Docker:

1. Build the Docker image:
   ```
   docker build -t nvidia-rag-chatbot-streamlit .
   ```

2. Run the container (make sure to provide your NVIDIA API key):
   ```
   docker run -p 8501:8501 -e NVIDIA_API_KEY='your_api_key_here' nvidia-rag-chatbot-streamlit
   ```

3. For a more complete setup with MongoDB, use Docker Compose:
   ```
   docker-compose up -d
   ```

## Project Structure

The project follows a modular architecture to ensure maintainability and extensibility:

- `app.py`: Main entry point for the Streamlit application
- `src/`: Source code directory
  - `auth/`: Authentication and user management
  - `database/`: Database interface and implementations
  - `document_processing/`: Document loading and processing
  - `llm/`: Language model integration
  - `ui/`: User interface components
  - `utils/`: Utility functions
  - `vector_store/`: Vector database integration
- `tests/`: Test suite
- `docs/`: Documentation

## Security Notes

1. Change the default admin password immediately after the first login.
2. For production use, ensure proper security measures are in place:
   - Use HTTPS
   - Secure database connections
   - Properly manage API keys
   - Regularly update dependencies

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- NVIDIA for providing the AI technologies used in this application.
- LlamaIndex for the powerful indexing and querying capabilities.
- Streamlit for the user interface framework.
- The original QnAChatbox project by John Flowers.