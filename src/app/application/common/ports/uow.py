from abc import ABC, abstractmethod
from types import TracebackType

from app.application.common.ports.repository import AsyncBaseRepository
from app.domain.entities.base import Entity
from app.domain.value_objects.entity_id import EntityId


class AsyncBaseUnitOfWork(ABC):
    @abstractmethod
    async def __aenter__(self) -> None:
        raise NotImplementedError("required __aenter__ call for UoW Pattern")

    async def __aexit__(
        self,
        exc_type: type[Exception] | None,
        exc_val: Exception | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type:
            await self.rollback()
        else:
            await self.commit()

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError("Choice ORM commit func")

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError("Choice ORM rollback func")

    @abstractmethod
    def repository[ET: Entity[EntityId]](
        self, entity: type[ET]
    ) -> AsyncBaseRepository[ET]:
        raise NotImplementedError("Choice ORM repository func")
