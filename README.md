# README: Insurance AI System - Enhanced Production Platform

## Overview

This repository contains the enhanced Insurance AI System, transformed from a CLI-based application into a production-ready API + UI platform. The system maintains all the original functionality while adding new features for asynchronous processing, event-driven architecture, and a web-based user interface.

## Key Features

- **Production-Grade API**: FastAPI implementation with proper schemas, validation, and OpenAPI documentation
- **Asynchronous Processing**: Celery with Redis for task queuing and background processing
- **Event-Driven Architecture**: Redis Streams for inter-agent communication with defined event contracts
- **Web UI**: Streamlit application for institution selection, data input, and real-time status tracking
- **Database Integration**: PostgreSQL with dynamic schema support and comprehensive migrations
- **Docker Support**: Multi-stage builds and Docker Compose for local development and production
- **Railway.com Deployment**: Ready-to-deploy configuration for Railway.com

## Architecture

The system is composed of the following components:

1. **API Server**: FastAPI application exposing endpoints for underwriting, claims, and actuarial analysis
2. **Celery Workers**: Background task processing for compute-intensive operations
3. **Event Broker**: Redis Streams for inter-agent communication
4. **Database**: PostgreSQL for structured data storage
5. **Web UI**: Streamlit application for user interaction

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.10+
- PostgreSQL 14+
- Redis 7+

### Local Development

1. Clone the repository
2. Set up environment variables (see `.env.example`)
3. Run the Docker Compose setup:

```bash
docker-compose up -d
```

4. Access the API at http://localhost:8080
5. Access the UI at http://localhost:8501

### Running Tests

```bash
python -m pytest tests.py
```

## Deployment

### Railway.com Deployment

1. Push the code to a Git repository
2. Connect the repository to Railway.com
3. Set the required environment variables
4. Deploy the application

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| POSTGRES_HOST | PostgreSQL host | localhost |
| POSTGRES_PORT | PostgreSQL port | 5432 |
| POSTGRES_DB | PostgreSQL database name | insurance_ai |
| POSTGRES_USER | PostgreSQL username | postgres |
| POSTGRES_PASSWORD | PostgreSQL password | postgres |
| DB_SCHEMA | Database schema name | insurance_ai |
| REDIS_HOST | Redis host | localhost |
| REDIS_PORT | Redis port | 6379 |
| REDIS_PASSWORD | Redis password | |
| REDIS_DB | Redis database number | 0 |
| API_PORT | API server port | 8080 |
| ALLOWED_ORIGINS | CORS allowed origins | * |

## API Documentation

Once the API is running, access the OpenAPI documentation at:

- Swagger UI: http://localhost:8080/docs

## Directory Structure

```
insurance_ai_system/
├── api.py                 # FastAPI application
├── celery_app.py          # Celery configuration
├── db_connection.py       # Database connection module
├── db_migrations.py       # Database migrations
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile             # Docker build configuration
├── event_listener.py      # Event listener service
├── events.py              # Event broker module
├── main.py                # Main entry point
├── railway.json           # Railway.com configuration
├── requirements.txt       # Python dependencies
├── schemas.py             # Pydantic schemas
├── tasks.py               # Celery tasks
├── tests.py               # Test suite
├── ui/                    # Streamlit UI
│   └── streamlit_app.py   # Streamlit application
└── utils/                 # Utility modules
    └── logging_utils.py   # Logging utilities
```

## Original Features Preserved

- Underwriting flow with risk assessment
- Claims processing with fraud detection
- Actuarial analysis with risk modeling
- Agent-based architecture
- Configuration management
- Audit logging

## New Features Added

- Asynchronous task processing
- Event-driven architecture
- Web-based user interface
- API with OpenAPI documentation
- Docker and Docker Compose support
- Railway.com deployment configuration
- Comprehensive test suite
