from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from app.application.common.query_params.pagination import Pagination
from app.application.common.query_params.sorting import Sorting
from app.domain.entities.base import Entity
from app.domain.value_objects.entity_id import EntityId


class AsyncBaseRepository[ET: Entity[EntityId]](ABC):
    @abstractmethod
    async def get(self, pk: EntityId) -> ET | None:
        pass

    @abstractmethod
    async def all(
        self,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
        **kwargs: Any,
    ) -> Sequence[ET]:
        pass

    @abstractmethod
    async def one(self, **kwargs: Any) -> ET | None:
        pass

    @abstractmethod
    async def exists(self, **kwargs: Any) -> bool:
        pass

    @abstractmethod
    def create(self, entity: ET) -> None:
        pass

    @abstractmethod
    async def create_all(self, entity: Sequence[ET]) -> None:
        pass

    @abstractmethod
    def update(self, entity: ET, data: dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def delete(self, entity: ET) -> None:
        pass
