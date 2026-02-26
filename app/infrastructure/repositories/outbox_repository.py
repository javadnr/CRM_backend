import json
from enum import Enum
from uuid import UUID
from datetime import datetime
from app.infrastructure.db.models.outbox_model import OutboxMessageModel

class OutboxRepository:

    def __init__(self, session):
        self.session = session

    def _serialize_event(self, event):
        payload = {}
        for key, value in event.__dict__.items():
            if isinstance(value, UUID):
                payload[key] = str(value)
            elif isinstance(value, Enum):
                payload[key] = value.value
            elif isinstance(value, datetime):
                payload[key] = value.isoformat()
            else:
                payload[key] = value
        return payload

    async def add_event(self, event):
        payload = self._serialize_event(event)

        message = OutboxMessageModel(
            event_type=event.__class__.__name__,
            payload=payload,
        )

        self.session.add(message)
        # optionally commit outside for transaction management