from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.infrastructure.repositories.lead_repository import LeadRepository
from app.application.services.dashboard_service import DashboardService
from app.api.schemas.common import PaginatedResponse
from app.infrastructure.cache.dashboard_cache import DashboardCache
from app.api.schemas.dashboard import (
    DashboardStatsResponse,
    LeadResponse,
)

router = APIRouter(prefix="/dashboard")

@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(session: AsyncSession = Depends(get_db)):
    try:
        repo = LeadRepository(session)
        cache = DashboardCache()
        service = DashboardService(repo,cache)

        stats = await service.get_stats()

        return DashboardStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail='Internal Server Error')

@router.get("/leads", response_model=PaginatedResponse[LeadResponse])
async def get_leads(
    source: str | None = Query(default=None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    try:
        repo = LeadRepository(session)
        cache = DashboardCache()
        service = DashboardService(repo,cache)

        items, total = await service.get_leads_paginated(
            source,
            page,
            page_size,
        )

        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail='Internal Server Error')