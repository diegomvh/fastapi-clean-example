import logging
from collections.abc import Mapping
from types import TracebackType
from typing import Any, cast

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSessionTransaction

from app.application.common.ports.repository import AsyncBaseRepository
from app.application.common.ports.uow import AsyncBaseUnitOfWork
from app.domain.entities.base import Entity
from app.domain.exceptions.user import UsernameAlreadyExistsError
from app.domain.value_objects.entity_id import EntityId
from app.infrastructure.adapters.constants import (
    DB_COMMIT_DONE,
    DB_COMMIT_FAILED,
    DB_CONSTRAINT_VIOLATION,
    DB_FLUSH_DONE,
    DB_FLUSH_FAILED,
    DB_QUERY_FAILED,
    DB_ROLLBACK_DONE,
    DB_ROLLBACK_FAILED,
)
from app.infrastructure.adapters.repository import AsyncSQLAlchemyRepository
from app.infrastructure.adapters.types import MainAsyncSession
from app.infrastructure.exceptions.gateway import DataMapperError

log = logging.getLogger(__name__)


class AsyncSQLAlchemyUnitOfWork(AsyncBaseUnitOfWork):
    def __init__(self, session: MainAsyncSession):
        self._session = session
        self._transaction: AsyncSessionTransaction | None = None

    @property
    def session(self) -> MainAsyncSession:
        if self._session is None:
            raise RuntimeError("Session is not initialized")
        return self._session

    async def __aenter__(self):
        self._transaction = await self.session.begin()

    async def __aexit__(
        self,
        exc_type: type[Exception] | None,
        exc_val: Exception | None,
        traceback: TracebackType | None,
    ) -> None:
        await super().__aexit__(exc_type, exc_val, traceback)

    async def commit(self):
        try:
            if self._transaction is not None:
                await self._transaction.commit()
                self._transaction = None
            else:
                await self.session.commit()
            log.debug("%s Main session.", DB_COMMIT_DONE)

        except SQLAlchemyError as error:
            raise DataMapperError(f"{DB_QUERY_FAILED} {DB_COMMIT_FAILED}") from error

    async def flush(self):
        """
        :raises DataMapperError:
        :raises UsernameAlreadyExists:
        """
        try:
            await self.session.flush()
            log.debug("%s Main session.", DB_FLUSH_DONE)

        except IntegrityError as error:
            if "uq_users_username" in str(error):
                params: Mapping[str, Any] = cast(Mapping[str, Any], error.params)
                username = str(params.get("username", "unknown"))
                raise UsernameAlreadyExistsError(username) from error

            raise DataMapperError(DB_CONSTRAINT_VIOLATION) from error

        except SQLAlchemyError as error:
            raise DataMapperError(f"{DB_QUERY_FAILED} {DB_FLUSH_FAILED}") from error

    async def refresh(self, item):
        await self.session.refresh(item)

    async def rollback(self):
        try:
            if self._transaction is not None:
                await self._transaction.rollback()
                self._transaction = None
            else:
                await self.session.rollback()
            log.debug("%s Main session.", DB_ROLLBACK_DONE)

        except SQLAlchemyError as error:
            raise DataMapperError(f"{DB_QUERY_FAILED} {DB_ROLLBACK_FAILED}") from error

    def repository[ET: Entity[EntityId]](
        self,
        model: type[ET],
    ) -> AsyncBaseRepository[ET]:
        return AsyncSQLAlchemyRepository[ET](model, self.session)
