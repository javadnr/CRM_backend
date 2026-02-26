from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from collections import defaultdict
from typing import Dict, List

from app.domain.interfaces.repositories import LeadRepositoryInterface
from app.infrastructure.db.models.lead_model import LeadModel

class LeadRepository(LeadRepositoryInterface):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, lead_id: UUID) -> LeadModel | None:
        result = await self.session.execute(
            select(LeadModel).where(LeadModel.id == lead_id)
        )
        return result.scalar_one_or_none()

    async def add(self, lead: LeadModel):
        self.session.add(lead)
        await self.session.flush()
    
    async def get_status_stats(self) -> Dict[str, int]:

        stmt = (
            select(
                LeadModel.status,
                func.count(LeadModel.id)
            )
            .group_by(LeadModel.status)
        )

        result = await self.session.execute(stmt)

        stats = defaultdict(int)

        for status, count in result.all():
            stats[status] = count

        return stats
    
    async def filter_by_source(
        self,
        source: str | None
    ) -> List[LeadModel]:

        stmt = select(LeadModel)

        if source:
            stmt = stmt.where(LeadModel.source == source)

        result = await self.session.execute(stmt)

        return result.scalars().all()