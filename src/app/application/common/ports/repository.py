from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from app.domain.entities.base import Entity
from app.domain.value_objects.entity_id import EntityId


class AsyncBaseRepository[ET: Entity[EntityId]](ABC):
    @abstractmethod
    async def find_by_pk(self, pk: EntityId) -> ET | None:
        pass

    @abstractmethod
    async def find_by_col(self, **kwargs: dict[str, Any]) -> ET | None:
        pass

    @abstractmethod
    async def find_all(self, **kwargs: dict[str, Any]) -> Sequence[ET]:
        pass

    @abstractmethod
    async def is_exists(self, **kwargs: dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def create(self, item: ET) -> None:
        pass

    @abstractmethod
    async def create_all(self, items: list[ET]) -> None:
        pass

    @abstractmethod
    def update(self, item: ET, req: dict[str, Any]) -> None:
        pass
