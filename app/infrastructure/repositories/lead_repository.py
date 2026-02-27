from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from uuid import UUID
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

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
        
    async def find_existing_lead(self, phone: str, email: str) -> bool:
        if not phone and not email:
            return False
        
        stmt = select(LeadModel)
        conditions = []

        if phone and phone.strip():
            clean_phone = phone.strip()
            conditions.append(LeadModel.phone == clean_phone)

        if email and email.strip():
            clean_email = email.strip().lower()
            conditions.append(func.lower(LeadModel.email) == clean_email)

        if not conditions:
            return False
        
        stmt = stmt.where(or_(*conditions))
        
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            return True
        else:
            return False

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
    
    async def filter_with_pagination(
        self,
        source: str | None,
        page: int,
        page_size: int,
    ):

        base_query = select(LeadModel)

        if source:
            base_query = base_query.where(
                LeadModel.source == source
            )

        count_stmt = select(func.count()).select_from(
            base_query.subquery()
        )

        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = (
            base_query
            .offset((page - 1) * page_size)
            .limit(page_size)
            .order_by(LeadModel.created_at.desc())
        )

        result = await self.session.execute(stmt)

        items = result.scalars().all()

        return items, total