from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import AsyncSessionLocal
from app.infrastructure.repositories.lead_repository import LeadRepository
from app.infrastructure.repositories.action_history_repository import (
    ActionHistoryRepository,
)
from app.domain.interfaces.unit_of_work import AbstractUnitOfWork
from app.infrastructure.repositories.outbox_repository import (
    OutboxRepository
)

class SQLAlchemyUnitOfWork(AbstractUnitOfWork):

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
            await self.rollback()
        else:
            await self.commit()

        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()