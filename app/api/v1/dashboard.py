from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import sys

from app.api.deps import get_dashboard_service
from app.infrastructure.repositories.lead_repository import LeadRepository
from app.application.services.dashboard_service import DashboardService
from app.api.schemas.common import PaginatedResponse
from app.infrastructure.cache.dashboard_cache import DashboardCache
from app.api.schemas.dashboard import (
    DashboardStatsResponse,
    LeadResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dashboard")

@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(service: DashboardService = Depends(get_dashboard_service)):
    try:

        stats = await service.get_stats()

        return DashboardStatsResponse(**stats)
    except Exception as e:
        exception_text = 'Error on line {}: {} - {}'.format(sys.exc_info()[-1].tb_lineno, type(e).__name__, e)
        logger.error(f"exception in /stats GET: {exception_text}")
        raise HTTPException(status_code=500, detail='Internal Server Error')

@router.get("/leads", response_model=PaginatedResponse[LeadResponse])
async def get_leads(
    source: str | None = Query(default=None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: DashboardService = Depends(get_dashboard_service),
):
    try:
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
        exception_text = 'Error on line {}: {} - {}'.format(sys.exc_info()[-1].tb_lineno, type(e).__name__, e)
        logger.error(f"exception in /leads GET: {exception_text}")
        raise HTTPException(status_code=500, detail='Internal Server Error')