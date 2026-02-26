import json
from app.infrastructure.db.models.outbox_model import (
    OutboxMessageModel,
)


class OutboxRepository:

    def __init__(self, session):
        self.session = session

    async def add_event(self, event):

        message = OutboxMessageModel(
            event_type=event.__class__.__name__,
            payload=event.__dict__,
        )

        self.session.add(message)