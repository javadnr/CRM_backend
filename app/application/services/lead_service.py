from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.infrastructure.repositories.lead_repository import LeadRepository
from app.infrastructure.repositories.action_history_repository import ActionHistoryRepository
from app.infrastructure.db.models.action_history_model import ActionHistoryModel
from app.domain.enums import LeadStatus
from app.infrastructure.cache.dashboard_cache import DashboardCache

class LeadNotFound(Exception):
    pass

class InvalidStatusTransition(Exception):
    pass

class LeadService:
    def __init__(
        self,
        lead_repo,
        history_repo,
        session,
        cache: DashboardCache,
    ):
        self.lead_repo = lead_repo
        self.history_repo = history_repo
        self.session = session
        self.cache = cache
        
    async def change_status(self, lead_id: UUID, new_status: LeadStatus):
        await self.cache.invalidate_stats()
        async with self.session.begin():  # atomic transaction
            # lock row
            result = await self.session.execute(
                select(self.lead_repo.session.bind.tables["leads"]).where(self.lead_repo.session.bind.tables["leads"].c.id == lead_id).with_for_update()
            )
            lead = await self.lead_repo.get_by_id(lead_id)
            if not lead:
                raise LeadNotFound()

            # business rules: terminal states cannot change
            if lead.status in (LeadStatus.CONVERTED, LeadStatus.LOST):
                raise InvalidStatusTransition(f"{lead.status} is terminal")

            old_status = lead.status
            lead.status = new_status

            history = ActionHistoryModel(
                lead_id=lead.id,
                from_status=old_status,
                to_status=new_status,
            )
            self.session.add(history)