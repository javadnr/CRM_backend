from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.infrastructure.repositories.lead_repository import LeadRepository
from app.application.services.dashboard_service import DashboardService
from app.api.schemas.dashboard import (
    DashboardStatsResponse,
    LeadResponse,
)

router = APIRouter(prefix="/dashboard")

@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    session: AsyncSession = Depends(get_db)
):

    repo = LeadRepository(session)
    service = DashboardService(repo)

    stats = await service.get_stats()

    return DashboardStatsResponse(**stats)


@router.get("/leads", response_model=list[LeadResponse])
async def get_leads(
    source: str | None = Query(default=None),
    session: AsyncSession = Depends(get_db)
):

    repo = LeadRepository(session)
    service = DashboardService(repo)

    leads = await service.get_leads(source)

    return leads