"""
Celery configuration for the Insurance AI System.
Sets up Celery with Redis as broker and result backend.
"""

import os
from celery import Celery

# Get Redis configuration from environment variables
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = os.environ.get('REDIS_PORT', '6379')
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', '')
REDIS_DB = os.environ.get('REDIS_DB', '0')

# Construct Redis URL
if REDIS_PASSWORD:
    REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
else:
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# Create Celery app
celery_app = Celery(
    'insurance_ai',
    broker=os.environ.get('CELERY_BROKER_URL', REDIS_URL),
    backend=os.environ.get('CELERY_RESULT_BACKEND', REDIS_URL),
    include=['tasks']  # Include tasks module
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes
    worker_prefetch_multiplier=1,  # Prevent worker from prefetching too many tasks
    task_acks_late=True,  # Acknowledge tasks after execution
)

# Optional: Configure task routes
celery_app.conf.task_routes = {
    'tasks.run_underwriting_task': {'queue': 'underwriting'},
    'tasks.run_claims_task': {'queue': 'claims'},
    'tasks.run_actuarial_task': {'queue': 'actuarial'},
    'tasks.generate_report_task': {'queue': 'reports'},
}

# Optional: Configure periodic tasks
celery_app.conf.beat_schedule = {
    'cleanup-old-tasks': {
        'task': 'tasks.cleanup_old_tasks',
        'schedule': 86400.0,  # Once per day
    },
}

if __name__ == '__main__':
    celery_app.start()
