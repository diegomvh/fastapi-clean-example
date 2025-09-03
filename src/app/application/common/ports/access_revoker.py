from abc import abstractmethod
from typing import Protocol

from app.domain.value_objects.entity_id import EntityId


class AccessRevoker(Protocol):
    @abstractmethod
    async def remove_all_user_access(self, user_id: EntityId) -> None:
        """
        :raises DataMapperError:
        """
