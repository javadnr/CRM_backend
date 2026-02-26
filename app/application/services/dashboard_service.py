from app.domain.interfaces.repositories import LeadRepositoryInterface


class DashboardService:

    def __init__(self, lead_repo: LeadRepositoryInterface):
        self.lead_repo = lead_repo

    async def get_stats(self):
        return await self.lead_repo.get_status_stats()

    async def get_leads(self, source: str | None):
        return await self.lead_repo.filter_by_source(source)