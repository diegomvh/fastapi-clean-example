from collections.abc import Sequence
from typing import Any

from sqlalchemy import Select, inspect, select

from app.application.common.ports.repository import AsyncBaseRepository
from app.application.common.query_params.pagination import Pagination
from app.application.common.query_params.sorting import Sorting, SortingOrder
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
        mapper = inspect(self._model)
        if mapper is None:
            raise RuntimeError("Model is not initialized")
        pk = mapper.primary_key
        if pk is None or len(pk) != 1:
            raise RuntimeError("Composite primary keys are not supported")
        return str(pk[0].name)

    async def get(self, pk: EntityId) -> ET | None:
        return await self.session.get(self._model, pk)

    async def one(self, **kwargs: Any) -> ET | None:
        query = await self.session.execute(self._gen_stmt_for_param(**kwargs))
        return query.unique().scalars().one_or_none()

    def _gen_stmt_for_param(self, **kwargs: Any) -> Select[tuple[ET]]:
        stmt = select(self._model)
        return stmt.filter_by(**kwargs)

    async def all(
        self,
        pagination: Pagination | None = None,
        sorting: Sorting | None = None,
        **kwargs: dict[str, Any],
    ) -> Sequence[ET]:
        stmt = self._gen_stmt_for_param(**kwargs)
        if sorting is not None:
            mapper = inspect(self._model)
            if mapper is None:
                raise RuntimeError("Model is not initialized")
            for column_attr in mapper.column_attrs:
                column = column_attr.columns[0]
            stmt = stmt.order_by(
                column.asc()
                if sorting.sorting_order == SortingOrder.ASC
                else column.desc()
            )
        if pagination is not None:
            stmt = stmt.limit(pagination.limit).offset(pagination.offset)
        result = await self.session.execute(stmt)

        return result.unique().scalars().fetchall()

    async def exists(self, **kwargs: Any) -> bool:
        result = await self.session.execute(
            self._gen_stmt_for_param(**kwargs).exists().select()
        )
        return result.scalar() is True

    def create(self, entity: ET) -> None:
        self.session.add(entity)

    async def create_all(self, entity: Sequence[ET]) -> None:
        self.session.add_all(entity)

    def update(self, entity: ET, data: dict[str, Any]) -> None:
        for k, v in data.items():
            if v is not None:
                setattr(entity, k, v)

    async def delete(self, entity: ET) -> None:
        await self.session.delete(entity)
