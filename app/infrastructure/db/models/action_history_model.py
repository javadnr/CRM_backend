import uuid
from sqlalchemy import Column, TIMESTAMP, func, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, ENUM
from app.infrastructure.db.base import Base
from app.domain.enums import LeadStatus

lead_status_enum = ENUM(
    LeadStatus,
    name="lead_status_enum",
    create_type=False
)

class ActionHistoryModel(Base):
    __tablename__ = "action_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True),ForeignKey("leads.id", ondelete="CASCADE"),nullable=False)
    from_status = Column(lead_status_enum, nullable=False)
    to_status = Column(lead_status_enum, nullable=False)
    changed_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index("idx_history_lead_id", "lead_id"),
    )