from sqlalchemy import select
from app.infrastructure.db.session import AsyncSessionLocal
from app.infrastructure.db.models.outbox_model import (
    OutboxMessageModel
)
from app.infrastructure.cache.dashboard_cache import (
    DashboardCache
)


async def process_outbox():

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(OutboxMessageModel)
            .where(OutboxMessageModel.processed == False)
        )

        events = result.scalars().all()

        cache = DashboardCache()

        for event in events:

            if event.event_type == "LeadStatusChangedEvent":
                await cache.invalidate_stats()

            event.processed = True

        await session.commit()