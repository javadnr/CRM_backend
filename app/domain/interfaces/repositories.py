from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, Dict, List, Tuple
from app.infrastructure.db.models.lead_model import LeadModel
from app.infrastructure.db.models.action_history_model import ActionHistoryModel
from app.domain.enums import LeadStatus


class LeadRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_id(self, lead_id: UUID) -> Optional[LeadModel]:
        ...

    @abstractmethod
    async def add(self, lead: LeadModel):
        ...
        
    @abstractmethod
    async def get_status_stats(self) -> Dict[str, int]:
        ...

    @abstractmethod
    async def filter_by_source(
        self,
        source: str | None
    ) -> List[LeadModel]:
        ...
        
    @abstractmethod
    async def filter_with_pagination(
        self,
        source: str | None,
        page: int,
        page_size: int,
    ) -> Tuple[List[LeadModel], int]:
        ...
class ActionHistoryRepositoryInterface(ABC):
    @abstractmethod
    async def add(self, history: ActionHistoryModel):
        ...