from app.domain.interfaces.repositories import LeadRepositoryInterface
from app.infrastructure.cache.dashboard_cache import DashboardCache

class DashboardService:

    def __init__(
        self,
        lead_repo: LeadRepositoryInterface,
        cache: DashboardCache,
    ):
        self.lead_repo = lead_repo
        self.cache = cache

    async def get_stats(self):
        """
        Sample of redis cache here to prevent database queries 
        in the future in higher traffics scenarios we can use 
        in other services too
        """
        cached = await self.cache.get_stats()
        if cached:
            return cached

        stats = await self.lead_repo.get_status_stats()

        await self.cache.set_stats(stats)

        return stats
    
    async def get_leads(self, source: str | None):
        #Todo add cache
        return await self.lead_repo.filter_by_source(source)
    
    async def get_leads_paginated(
        self,
        source: str | None,
        page: int,
        page_size: int,
    ):
        #Todo add cache
        return await self.lead_repo.filter_with_pagination(
            source,
            page,
            page_size,
        )