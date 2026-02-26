from datetime import datetime
from uuid import uuid4


class DomainEvent:
    def __init__(self):
        self.id = uuid4()
        self.occurred_at = datetime.utcnow()