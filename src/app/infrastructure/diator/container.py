from typing import Type, TypeVar  # noqa: UP035

from diator.container.protocol import Container
from dishka.async_container import AsyncContainer

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
        if not self._external_container:
            raise AttributeError
        return await self._external_container.get(type_)
