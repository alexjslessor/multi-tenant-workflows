from celery.app import Celery
from celery import Celery
from .settings import get_settings

settings = get_settings()

celery = Celery(
    'api',
    broker=settings.REDIS_URL, 
    backend=settings.REDIS_URL,
    include=["api.tasks"],
)
celery.conf.update(
    result_expires=3600,
)