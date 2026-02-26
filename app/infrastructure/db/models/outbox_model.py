import uuid
from sqlalchemy import Column, String, JSON, Boolean, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.infrastructure.db.base import Base


class OutboxMessageModel(Base):
    __tablename__ = "outbox_messages"

    id = Column(UUID(as_uuid=True),
                primary_key=True,
                default=uuid.uuid4)

    event_type = Column(String, nullable=False)

    payload = Column(JSON, nullable=False)

    processed = Column(Boolean,
                       default=False,
                       nullable=False)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )