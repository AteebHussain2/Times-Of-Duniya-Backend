# Dockerfile
FROM python:3.11-slim

# Install system packages
RUN apt-get update && apt-get install -y gcc

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run worker by default (can override in docker-compose)
CMD ["python", "worker.py"]
