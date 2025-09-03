from abc import abstractmethod
from typing import Protocol

from app.domain.value_objects.entity_id import EntityId


class IdentityProvider(Protocol):
    @abstractmethod
    async def get_current_user_id(self) -> EntityId:
        """
        :raises AuthenticationError:
        """
