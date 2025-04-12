import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'athAIna_backend.settings')
app = Celery('athAIna_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.update(
    broker_url='redis://redis:6379/0',
    result_backend='redis://redis:6379/0',
    accept_content=['json'],
    task_serializer='json',
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    broker_connection_retry_on_startup=True,  # Add this line
)