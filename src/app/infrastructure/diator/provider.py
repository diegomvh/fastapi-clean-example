import logging

from diator.events import EventEmitter, EventMap
from diator.mediator import Mediator
from diator.middlewares import MiddlewareChain

# from redis import asyncio as redis  # noqa: ERA001
from diator.requests import RequestMap

# from diator.message_brokers.redis import RedisMessageBroker  # noqa: ERA001
from fastapi import Request

from app.application.features.meeting.commands.join import (
    JoinMeetingCommandHandler,
    JoinMeetingCommandRequest,
)
from app.application.features.user.queries.list import (
    ListUsersQueryHandler,
    ListUsersQueryRequest,
)
from app.infrastructure.diator.container import DishkaContainer
from app.setup.config.settings import AppSettings

log = logging.getLogger(__name__)


def get_mediator(
    request: Request,
    settings: AppSettings,  # noqa: ARG001
) -> Mediator:
    dishka = DishkaContainer()
    dishka.attach_external_request(request)

    # Middlewares
    m_chain = MiddlewareChain()

    # Events
    # redis_client: redis.Redis = redis.Redis.from_url("redis://localhost:6379/0")  # noqa: E501, ERA001
    # message_broker = RedisMessageBroker(redis_client)  # noqa: ERA001
    e_map = EventMap()

    event_emitter = EventEmitter(event_map=e_map, container=dishka, message_broker=None)

    # Requests
    r_map = RequestMap()
    # Commands
    r_map.bind(JoinMeetingCommandRequest, JoinMeetingCommandHandler)
    # Queries
    r_map.bind(ListUsersQueryRequest, ListUsersQueryHandler)

    log.debug("Mediator initialized.")
    return Mediator(
        request_map=r_map,
        event_emitter=event_emitter,
        container=dishka,
        middleware_chain=m_chain,
    )
