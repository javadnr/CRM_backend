from uuid import UUID, uuid4
import logging

from app.domain.enums import LeadStatus
from app.infrastructure.db.models.action_history_model import (
    ActionHistoryModel,
)
from app.domain.interfaces.unit_of_work import AbstractUnitOfWork
from app.infrastructure.cache.dashboard_cache import DashboardCache
from app.infrastructure.db.models.lead_model import LeadModel
from app.core.exceptions.services import LeadNotFound, InvalidStatusTransition, LeadAlreadyExists, RepitiveStatusChange
logger = logging.getLogger(__name__)

class LeadService:

    def __init__(self, cache: DashboardCache):
        self.cache = cache
        
    async def create_lead(
        self,
        name: str,
        phone: str | None,
        email: str | None,
        source: str | None,
        uow: AbstractUnitOfWork,
    ):
        exsisting = await uow.leads.find_existing_lead(phone=phone,email=email)
        if exsisting == True:
            logger.debug(f"Lead with info {name,phone,email,source} already exists")
            raise LeadAlreadyExists()
        
        lead = LeadModel(
            id=uuid4(),
            name=name,
            phone=phone,
            email=email,
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
            logger.info(f"Lead with id {lead_id} not found")
            raise LeadNotFound()

        if lead.status in (
            LeadStatus.CONVERTED,
            LeadStatus.LOST,
        ):
            logger.info(f"Lead status with id: {lead_id} and status: {lead.status} cannot be changed")
            raise InvalidStatusTransition()

        old_status = lead.status
        lead.status = new_status

        if old_status == new_status:
            raise RepitiveStatusChange()
        history = ActionHistoryModel(
            lead_id=lead.id,
            from_status=old_status,
            to_status=new_status,
        )

        await uow.history.add(history)
        
        #example of using outbox model for other jobs like sending emails or caching
        # event = LeadStatusChangedEvent(
        #     lead.id,
        #     old_status,
        #     new_status,
        # )
        # await uow.outbox.add_event(event)
        
