from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "crm_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)
import app.workers.outbox_tasks
celery_app.conf.beat_schedule = {
    "process-outbox-every-30-sec": {
        "task": "process_outbox_task",
        "schedule": 30.0,  # seconds
    },
}
celery_app.conf.timezone = "UTC"