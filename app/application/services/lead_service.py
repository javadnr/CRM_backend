from uuid import UUID
from app.domain.enums import LeadStatus
from app.infrastructure.db.models.action_history_model import (
    ActionHistoryModel,
)
from app.domain.interfaces.unit_of_work import AbstractUnitOfWork
from app.infrastructure.cache.dashboard_cache import DashboardCache
from app.domain.events.lead_events import (
    LeadStatusChangedEvent
)
from uuid import uuid4
from app.infrastructure.db.models.lead_model import LeadModel
class LeadNotFound(Exception):
    pass


class InvalidStatusTransition(Exception):
    pass


class LeadService:

    def __init__(self, cache: DashboardCache):
        self.cache = cache
        
    async def create_lead(
        self,
        name: str,
        phone: str | None,
        source: str | None,
        uow: AbstractUnitOfWork,
    ):
        lead = LeadModel(
            id=uuid4(),
            name=name,
            phone=phone,
            source=source,
            status=LeadStatus.NEW,
        )
        await uow.leads.add(lead)
        return lead
    
    async def change_status(
        self,
        lead_id: UUID,
        new_status: LeadStatus,
        uow: AbstractUnitOfWork,
    ):

        lead = await uow.leads.get_by_id(lead_id)

        if not lead:
            raise LeadNotFound()

        if lead.status in (
            LeadStatus.CONVERTED,
            LeadStatus.LOST,
        ):
            raise InvalidStatusTransition()

        old_status = lead.status
        lead.status = new_status

        history = ActionHistoryModel(
            lead_id=lead.id,
            from_status=old_status,
            to_status=new_status,
        )

        await uow.history.add(history)
        
        event = LeadStatusChangedEvent(
            lead.id,
            old_status,
            new_status,
        )
        #example of using outbox model for other jobs like sending emails or caching
        # await uow.outbox.add_event(event)
        
