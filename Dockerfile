# Dockerfile for Data Pipeline Monitoring Dashboard
# This file defines how to build a Docker container for the application

# Use Python 3.11 as the base image
FROM python:3.11-slim

# Set working directory inside the container
# All commands will run from this directory
WORKDIR /app

# Set environment variables
# Prevents Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Install system dependencies
# These are needed for some Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first
# This allows Docker to cache the pip install step
# If requirements.txt changes, only this layer needs to be rebuilt
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir reduces image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code
# This happens after installing dependencies for better caching
COPY . .

# Create necessary directories
RUN mkdir -p data logs

# Expose port 5000
# This tells Docker which port the application will use
EXPOSE 5000

# Set the command to run when container starts
# This starts the Flask application
CMD ["python", "app.py"]
