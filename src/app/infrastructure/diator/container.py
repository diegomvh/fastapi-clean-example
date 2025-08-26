from typing import Type, TypeVar  # noqa: UP035

from diator.container.protocol import Container
from dishka import Scope
from dishka.async_container import AsyncContainer
from fastapi import Request

T = TypeVar("T")


class DishkaContainer(Container[AsyncContainer]):
    def __init__(self) -> None:
        self._external_container: AsyncContainer | None = None

    @property
    def external_container(self) -> AsyncContainer:
        if not self._external_container:
            raise AttributeError

        return self._external_container

    def attach_external_container(self, container: AsyncContainer) -> None:
        self._external_container = container

    async def resolve(self, type_: Type[T]) -> T:  # noqa: UP006
        async with self.external_container(
            scope=Scope.REQUEST, context={Request: self.external_container.get(Request)}
        ) as container:
            return await container.get(type_)
