from pydantic import BaseModel
from uuid import UUID


class LeadCreateRequest(BaseModel):
    name: str
    phone: str | None = None
    source: str | None = None

class LeadResponse(BaseModel):
    id: UUID
    name: str
    status: str
    