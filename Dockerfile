FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV CONFIG_DIR=/app/insurance_ai_system/config

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "insurance_ai_system/main.py", "--module", "all", "--institution", "institution_a"]

# For production deployment, you might want to use gunicorn or uvicorn
# CMD ["gunicorn", "-b", "0.0.0.0:8000", "insurance_ai_system.api:app"]
