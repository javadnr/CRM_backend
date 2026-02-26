from uuid import UUID
from app.domain.events.base import DomainEvent
from app.domain.enums import LeadStatus


class LeadStatusChangedEvent(DomainEvent):

    def __init__(
        self,
        lead_id: UUID,
        old_status: LeadStatus,
        new_status: LeadStatus,
    ):
        super().__init__()
        self.lead_id = lead_id
        self.old_status = old_status
        self.new_status = new_status