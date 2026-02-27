from sqlalchemy.ext.asyncio import AsyncSession
import logging 

from app.infrastructure.db.session import AsyncSessionLocal
from app.infrastructure.repositories.lead_repository import LeadRepository
from app.infrastructure.repositories.action_history_repository import (
    ActionHistoryRepository,
)
from app.domain.interfaces.unit_of_work import AbstractUnitOfWork
from app.infrastructure.repositories.outbox_repository import (
    OutboxRepository
)

logger = logging.getLogger(__name__)
class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    """
    Created context manager to handle transactions and rollbacks\n
    to achive atomic transactions to db bt sharing the same session
    in each repository at the same time 
    """
    def __init__(self):
        self.session: AsyncSession | None = None

    async def __aenter__(self):
        self.session = AsyncSessionLocal()
        self.outbox = OutboxRepository(self.session)

        self.leads = LeadRepository(self.session)
        self.history = ActionHistoryRepository(self.session)

        return await super().__aenter__()

    async def __aexit__(self, exc_type, exc, tb):

        if exc_type:
            logger.debug(f"A request to change the stat of a lead rolled back due to exception:{exc}")
            await self.rollback()
        else:
            await self.commit()

        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()