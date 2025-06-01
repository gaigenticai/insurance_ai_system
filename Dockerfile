"""
Dockerfile for the Insurance AI System.
Multi-stage build for API, worker, and UI components.
"""

# Base stage with common dependencies
FROM python:3.10-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# API stage
FROM base AS api
EXPOSE 8080
CMD ["python", "api.py"]

# Worker stage for Celery workers
FROM base AS worker
CMD ["celery", "-A", "celery_app", "worker", "--loglevel=info"]

# UI stage for Streamlit
FROM base AS ui
EXPOSE 8501
RUN pip install --no-cache-dir streamlit plotly pandas
CMD ["streamlit", "run", "ui/streamlit_app.py"]

# Production stage - default target
FROM api AS production
# Initialize the database on startup
CMD ["sh", "-c", "python db_migrations.py && python api.py"]
