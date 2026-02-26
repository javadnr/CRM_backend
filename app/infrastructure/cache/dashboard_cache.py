import json
from typing import Dict
from app.infrastructure.cache.redis import redis_client
from app.infrastructure.cache.keys import DASHBOARD_STATS_KEY


class DashboardCache:

    async def get_stats(self) -> Dict | None:
        data = await redis_client.get(DASHBOARD_STATS_KEY)

        if not data:
            return None

        return json.loads(data)

    async def set_stats(self, stats: Dict):
        await redis_client.set(
            DASHBOARD_STATS_KEY,
            json.dumps(stats),
            ex=60  # TTL 60 seconds
        )

    async def invalidate_stats(self):
        await redis_client.delete(DASHBOARD_STATS_KEY)