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

    def attach_external_request(self, request: Request) -> None:
        self._external_request = request
        self.attach_external_container(request.app.state.dishka_container)

    async def resolve(self, type_: Type[T]) -> T:  # noqa: UP006
        if not self._external_container or not self._external_request:
            raise AttributeError
        async with self._external_container(
            scope=Scope.REQUEST, context={Request: self._external_request}
        ) as container:
            return await container.get(type_)
