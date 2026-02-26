from fastapi import APIRouter, HTTPException
from uuid import UUID

from app.infrastructure.db.unit_of_work import SQLAlchemyUnitOfWork
from app.application.services.lead_service import LeadService, LeadNotFound, InvalidStatusTransition
from app.infrastructure.cache.dashboard_cache import DashboardCache
from app.domain.enums import LeadStatus
from app.api.schemas.leads import LeadCreateRequest, LeadCreateResponse

router = APIRouter()
cache = DashboardCache()
service = LeadService(cache)
    
@router.post("/leads", response_model=LeadCreateResponse)
async def create_lead(req: LeadCreateRequest):
    try:
        async with SQLAlchemyUnitOfWork() as uow:
            lead = await service.create_lead(
                name=req.name,
                phone=req.phone,
                source=req.source,
                uow=uow
            )
        return LeadCreateResponse(
            id=lead.id,
            name=lead.name,
            status=lead.status.value
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail='Internal Server Error')
    
@router.post("/leads/{lead_id}/status")
async def update_status(lead_id: UUID, new_status: LeadStatus):
    try:
        async with SQLAlchemyUnitOfWork() as uow:
            await service.change_status(
                lead_id,
                new_status,
                uow,
            )

        return {"status": "updated"}
    except LeadNotFound:
        raise HTTPException(status_code=404, detail='Lead not found')
    
    except InvalidStatusTransition:
        raise HTTPException(status_code=400, detail='Invalid status transition')
    
    except Exception as e:
        raise HTTPException(status_code=500, detail='Internal Server Error')
