from uuid import UUID
from app.domain.enums import LeadStatus
from app.infrastructure.db.models.action_history_model import (
    ActionHistoryModel,
)
from app.domain.interfaces.unit_of_work import AbstractUnitOfWork
from app.infrastructure.cache.dashboard_cache import DashboardCache


class LeadNotFound(Exception):
    pass


class InvalidStatusTransition(Exception):
    pass


class LeadService:

    def __init__(self, cache: DashboardCache):
        self.cache = cache

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

        # cache invalidation AFTER successful transaction
        await self.cache.invalidate_stats()