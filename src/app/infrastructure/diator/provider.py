import logging

from diator.containers.dishka import DishkaContainer
from diator.events import EventEmitter
from diator.mediator import Mediator
from diator.middlewares import MiddlewareChain
from dishka import AsyncContainer

# from redis import asyncio as redis  # noqa: ERA001
# from diator.message_brokers.redis import RedisMessageBroker  # noqa: ERA001
from app.application.cqrs import event_map, request_map
from app.setup.config.settings import AppSettings

log = logging.getLogger(__name__)


def get_mediator(
    container: AsyncContainer,
    settings: AppSettings,  # noqa: ARG001
) -> Mediator:
    dishka = DishkaContainer()
    dishka.attach_external_container(container)

    # Middlewares
    m_chain = MiddlewareChain()

    # Events
    # redis_client: redis.Redis = redis.Redis.from_url("redis://localhost:6379/0")  # noqa: E501, ERA001
    # message_broker = RedisMessageBroker(redis_client)  # noqa: ERA001

    event_emitter = EventEmitter(
        event_map=event_map, container=dishka, message_broker=None
    )

    log.debug("Mediator initialized.")
    return Mediator(
        request_map=request_map,
        event_emitter=event_emitter,
        container=dishka,
        middleware_chain=m_chain,
    )
