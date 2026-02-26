from celery import shared_task
import asyncio

from app.workers.outbox_worker import process_outbox

@shared_task(name="process_outbox_task")
def process_outbox_task():
    asyncio.run(process_outbox())