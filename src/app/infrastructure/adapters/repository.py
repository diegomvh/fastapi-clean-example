from collections.abc import Sequence
from typing import Any

from sqlalchemy import Select, inspect, select

from app.application.common.ports.repository import AsyncBaseRepository
from app.domain.entities.base import Entity
from app.domain.value_objects.entity_id import EntityId
from app.infrastructure.adapters.types import MainAsyncSession


class AsyncSQLAlchemyRepository[
    ET: Entity[EntityId],
](AsyncBaseRepository[ET]):
    def __init__(self, model: type[ET], session: MainAsyncSession):
        self._model: type[ET] = model
        self._session = session

    @property
    def session(self) -> MainAsyncSession:
        if self._session is None:
            raise RuntimeError("Session is not initialized")
        return self._session

    @property
    def _pk_column(self) -> str:
        ins = inspect(self._model)
        if ins is None:
            raise RuntimeError("Model is not initialized")
        pk = ins.primary_key
        if pk is None or len(pk) != 1:
            raise RuntimeError("Composite primary keys are not supported")
        return str(pk[0].name)

    async def find_by_pk(self, pk: EntityId) -> ET | None:
        return await self.session.get(self._model, pk)

    async def find_by_col(self, **kwargs: dict[str, Any]) -> ET | None:
        item = await self.session.execute(self._gen_stmt_for_param(**kwargs))
        return item.unique().scalars().one_or_none()

    def _gen_stmt_for_param(self, **kwargs: dict[str, Any]) -> Select[tuple[ET]]:
        stmt = select(self._model)
        return stmt.filter_by(**kwargs)

    async def find_all(self, **kwargs: dict[str, Any]) -> Sequence[ET]:
        stmt = self._gen_stmt_for_param(**kwargs)
        result = await self.session.execute(stmt)

        return result.unique().scalars().fetchall()

    async def is_exists(self, **kwargs: dict[str, Any]) -> bool:
        result = await self.session.execute(
            self._gen_stmt_for_param(**kwargs).exists().select()
        )
        return result.scalar() is True

    def create(self, item: ET) -> None:
        self.session.add(item)

    async def create_all(self, items: list[ET]) -> None:
        self.session.add_all(items)

    def update(self, item: ET, req: dict[str, Any]) -> None:
        for k, v in req.items():
            if v is not None:
                setattr(item, k, v)

    async def delete(self, item: ET) -> None:
        await self.session.delete(item)
