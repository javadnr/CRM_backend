from abc import ABC, abstractmethod
from app.domain.interfaces.repositories import (
    LeadRepositoryInterface,
    ActionHistoryRepositoryInterface,
)


class AbstractUnitOfWork(ABC):

    leads: LeadRepositoryInterface
    history: ActionHistoryRepositoryInterface

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