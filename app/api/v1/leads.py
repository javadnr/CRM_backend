from fastapi import APIRouter, HTTPException, Request, Depends
from uuid import UUID
import logging
import sys

from app.infrastructure.db.unit_of_work import SQLAlchemyUnitOfWork
from app.application.services.lead_service import LeadService
from app.core.exceptions.services import LeadNotFound, InvalidStatusTransition,LeadAlreadyExists,RepitiveStatusChange
from app.domain.enums import LeadStatus
from app.api.schemas.leads import LeadCreateRequest, LeadCreateResponse
from app.api.deps import get_lead_service

logger = logging.getLogger(__name__)
router = APIRouter()

    
@router.post("/leads", response_model=LeadCreateResponse)
async def create_lead(req: LeadCreateRequest, service: LeadService = Depends(get_lead_service)):
    try:
        async with SQLAlchemyUnitOfWork() as uow:
            lead = await service.create_lead(
                name=req.name,
                phone=req.phone,
                email=req.email,
                source=req.source,
                uow=uow
            )
        return LeadCreateResponse(
            id=lead.id,
            name=lead.name,
            status=lead.status.value
        )
    except LeadAlreadyExists:
        raise HTTPException(status_code=400, detail='Lead already exists')
    
    except Exception as e:
        exception_text = 'Error on line {}: {} - {}'.format(sys.exc_info()[-1].tb_lineno, type(e).__name__, e)
        logger.error(f"exception in /leads POST: {exception_text}")
        raise HTTPException(status_code=500, detail='Internal Server Error')
    
@router.post("/leads/{lead_id}/status")
async def update_status(lead_id: UUID, new_status: LeadStatus, request: Request,service: LeadService = Depends(get_lead_service)):
    try:
        async with SQLAlchemyUnitOfWork() as uow:
            await service.change_status(
                lead_id,
                new_status,
                uow,
            )

        return {"status": "updated"}
    
    except RepitiveStatusChange:
        raise HTTPException(status_code=400, detail='Invalid status transition for lead repitive status change')
    
    except LeadNotFound:
        #TODO add report mechanism to admin to prevent malicious requests
        logger.warning(f"A request with ip:{request.client.host} came to change lead status with id:{lead_id} and new status:{new_status} but lead not found")
        raise HTTPException(status_code=404, detail='Lead ID not found')
    
    except InvalidStatusTransition:
        #TODO add report mechanism to admin to prevent malicious requests
        logger.warning(f"A request with ip:{request.client.host} came to change lead status with id:{lead_id} and new status:{new_status} but lead status is invalid")
        raise HTTPException(status_code=400, detail='Invalid status transition for lead converted and lost cannot be changed')
    
    except Exception as e:
        exception_text = 'Error on line {}: {} - {}'.format(sys.exc_info()[-1].tb_lineno, type(e).__name__, e)
        logger.error(f"exception in /leads/id/statis POST: {exception_text}")
        raise HTTPException(status_code=500, detail='Internal Server Error')
