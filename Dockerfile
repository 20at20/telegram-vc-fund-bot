# Dockerfile for containerized deployment (optional alternative to Railway)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install Node.js (for MCP servers)
RUN apt-get update && \
    apt-get install -y nodejs npm && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for credentials
RUN mkdir -p config/credentials

# Run the bot
CMD ["python", "src/main.py"]
