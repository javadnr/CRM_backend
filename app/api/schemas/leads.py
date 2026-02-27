from pydantic import BaseModel
from uuid import UUID


class LeadCreateRequest(BaseModel):
    name: str
    phone: str | None = None
    email: str | None = None
    source: str | None = None

class LeadCreateResponse(BaseModel):
    id: UUID
    name: str
    status: str
    