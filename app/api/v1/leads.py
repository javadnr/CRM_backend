from fastapi import APIRouter
from uuid import UUID

from app.infrastructure.db.unit_of_work import SQLAlchemyUnitOfWork
from app.application.services.lead_service import LeadService
from app.infrastructure.cache.dashboard_cache import DashboardCache
from app.domain.enums import LeadStatus
from app.api.schemas.leads import LeadCreateRequest, LeadResponse

router = APIRouter()
cache = DashboardCache()
service = LeadService(cache)

@router.post("/leads/{lead_id}/status")
async def update_status(
    lead_id: UUID,
    new_status: LeadStatus,
):
    async with SQLAlchemyUnitOfWork() as uow:
        await service.change_status(
            lead_id,
            new_status,
            uow,
        )

    return {"status": "updated"}

    
@router.post("/leads", response_model=LeadResponse)
async def create_lead(req: LeadCreateRequest):
    async with SQLAlchemyUnitOfWork() as uow:
        lead = await service.create_lead(
            name=req.name,
            phone=req.phone,
            source=req.source,
            uow=uow
        )
    return LeadResponse(
        id=lead.id,
        name=lead.name,
        status=lead.status.value
    )