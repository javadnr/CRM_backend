from fastapi import APIRouter
from uuid import UUID

from app.infrastructure.db.unit_of_work import SQLAlchemyUnitOfWork
from app.application.services.lead_service import LeadService
from app.infrastructure.cache.dashboard_cache import DashboardCache
from app.domain.enums import LeadStatus

router = APIRouter()

@router.post("/leads/{lead_id}/status")
async def update_status(
    lead_id: UUID,
    new_status: LeadStatus,
):

    cache = DashboardCache()
    service = LeadService(cache)

    async with SQLAlchemyUnitOfWork() as uow:
        await service.change_status(
            lead_id,
            new_status,
            uow,
        )

    return {"status": "updated"}