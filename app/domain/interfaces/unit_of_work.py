from abc import ABC, abstractmethod
from app.domain.interfaces.repositories import (
    LeadRepositoryInterface,
    ActionHistoryRepositoryInterface,
    OutboxRepositoryInterface
)


class AbstractUnitOfWork(ABC):

    leads: LeadRepositoryInterface
    history: ActionHistoryRepositoryInterface
    outbox: OutboxRepositoryInterface
    
    async def __aenter__(self):
        return self

    @abstractmethod
    async def __aexit__(self, exc_type, exc, tb):
        ...

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...