
import uuid
from sqlalchemy import Column, String, TIMESTAMP, func, Index
from sqlalchemy.dialects.postgresql import UUID, ENUM
from app.infrastructure.db.base import Base
from app.domain.enums import LeadStatus

lead_status_enum = ENUM(
    LeadStatus,
    name="lead_status_enum",
    create_type=True
)

class LeadModel(Base):
    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False, default='')
    source = Column(String, nullable=False)
    status = Column(lead_status_enum, nullable=False, default=LeadStatus.NEW.value)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_leads_status", "status"),
        Index("idx_leads_source", "source"),
    )