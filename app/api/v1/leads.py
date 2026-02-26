from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.deps import get_db
from app.infrastructure.repositories.lead_repository import LeadRepository
from app.infrastructure.repositories.action_history_repository import ActionHistoryRepository
from app.application.services.lead_service import LeadService
from app.domain.enums import LeadStatus

router = APIRouter()

@router.post("/leads/{lead_id}/status")
async def update_lead_status(lead_id: str, new_status: LeadStatus, session: AsyncSession = Depends(get_db)):
    lead_repo = LeadRepository(session)
    history_repo = ActionHistoryRepository(session)
    service = LeadService(lead_repo, history_repo, session)
    await service.change_status(UUID(lead_id), new_status)
    return {"status": "ok"}