"""
Utility module for initializing the application.
Ensures all required directories and files exist.
"""

import os
import logging
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

def ensure_directories():
    """
    Ensure all required directories exist.
    Creates them if they don't exist.
    """
    # List of directories to ensure
    directories = [
        'logs',
        'config',
        'data',
        'ui/assets'
    ]
    
    # Create directories
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Ensured directory exists: {directory}")

def initialize_app():
    """
    Initialize the application.
    Ensures all required directories and files exist.
    """
    # Ensure directories
    ensure_directories()
    
    # Create empty .env file if it doesn't exist
    env_file = '.env'
    if not os.path.exists(env_file):
        with open(env_file, 'w') as f:
            f.write("# Environment variables for Insurance AI System\n")
            f.write("POSTGRES_HOST=localhost\n")
            f.write("POSTGRES_PORT=5432\n")
            f.write("POSTGRES_DB=insurance_ai\n")
            f.write("POSTGRES_USER=postgres\n")
            f.write("POSTGRES_PASSWORD=postgres\n")
            f.write("DB_SCHEMA=insurance_ai\n")
            f.write("REDIS_HOST=localhost\n")
            f.write("REDIS_PORT=6379\n")
            f.write("REDIS_PASSWORD=\n")
            f.write("REDIS_DB=0\n")
            f.write("API_PORT=8080\n")
            f.write("ALLOWED_ORIGINS=*\n")
        
        logger.info(f"Created .env file: {env_file}")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize app
    initialize_app()
