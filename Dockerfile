# Video Tools Bot - Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (FFmpeg and other required packages)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Create downloads directory
RUN mkdir -p downloads

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "main.py"]