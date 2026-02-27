from app.infrastructure.db.session import AsyncSessionLocal
from app.infrastructure.cache.dashboard_cache import DashboardCache
from app.application.services.lead_service import LeadService
from app.infrastructure.repositories.lead_repository import LeadRepository
from app.application.services.dashboard_service import DashboardService

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
        

async def get_lead_service():
    cache = DashboardCache()
    service = LeadService(cache)
    yield service
    
async def get_dashboard_service():
    async with AsyncSessionLocal() as session:
        repo = LeadRepository(session)
        cache = DashboardCache()
        service = DashboardService(repo,cache) 
        yield service