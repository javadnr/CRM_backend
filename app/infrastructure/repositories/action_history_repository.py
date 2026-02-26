from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.interfaces.repositories import (
    ActionHistoryRepositoryInterface
)
from app.infrastructure.db.models.action_history_model import ActionHistoryModel


class ActionHistoryRepository(ActionHistoryRepositoryInterface):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, history: ActionHistoryModel):
        self.session.add(history)
        await self.session.flush()