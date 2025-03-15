FROM python:3.9-slim

WORKDIR /app

# Install security updates and curl for healthcheck
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/db

# Create a non-root user to run the application
RUN useradd -m appuser

# Copy application files
COPY . .

# Set environment variables
ENV NVIDIA_API_KEY=""
ENV ADMIN_USERNAME="admin"
ENV ADMIN_PASSWORD="admin@123"
ENV SESSION_EXPIRY_MINUTES=30
ENV MAX_LOGIN_ATTEMPTS=5
ENV IP_COOLDOWN_MINUTES=15
ENV DB_TYPE="sqlite"
ENV SQLITE_DB_PATH="/app/db/qnachat.db"

# Create necessary directories and files
RUN touch user_activity.json
RUN touch users.yaml

# Set proper permissions
RUN chown -R appuser:appuser /app
RUN chmod 600 /app/users.yaml

# Switch to non-root user
USER appuser

# Expose port for Streamlit
EXPOSE 8501

# Run the application with security options
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=true"]
