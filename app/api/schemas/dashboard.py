from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


class DashboardStatsResponse(BaseModel):
    new: int = 0
    in_progress: int = 0
    converted: int = 0
    lost: int = 0


class LeadResponse(BaseModel):
    id: UUID
    name: str
    phone: str
    source: str
    status: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,

    )