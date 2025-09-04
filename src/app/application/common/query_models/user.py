from typing import TypedDict
from uuid import UUID

from app.domain.entities.base import Entity
from app.domain.enums.user_role import UserRole
from app.domain.value_objects.entity_id import EntityId


class UserQueryModel(TypedDict):
    id_: UUID
    username: str
    role: UserRole
    is_active: bool


class Query[E: Entity[EntityId]](TypedDict):
    pass
