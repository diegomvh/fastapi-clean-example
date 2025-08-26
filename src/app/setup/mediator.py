from diator.events import EventEmitter, EventMap
from diator.mediator import Mediator
from diator.middlewares import MiddlewareChain

# from redis import asyncio as redis  # noqa: ERA001
from diator.requests import RequestMap
from dishka import AsyncContainer

# from diator.message_brokers.redis import RedisMessageBroker  # noqa: ERA001
from fastapi import FastAPI

from app.application.features.meeting.commands.join import (
    JoinMeetingCommand,
    JoinMeetingCommandHandler,
)
from app.infrastructure.diator.container import DishkaContainer
from app.setup.config.settings import AppSettings


def setup_mediator(
    container: AsyncContainer,
    settings: AppSettings,  # noqa: ARG001
    app: FastAPI,
) -> None:
    diska = DishkaContainer()
    diska.attach_external_container(container)

    # Middlewares
    middleware_chain = MiddlewareChain()

    # Events
    # redis_client: redis.Redis = redis.Redis.from_url("redis://localhost:6379/0")  # noqa: E501, ERA001
    # message_broker = RedisMessageBroker(redis_client)  # noqa: ERA001
    event_map = EventMap()

    event_emitter = EventEmitter(
        event_map=event_map, container=diska, message_broker=None
    )

    # Requests
    request_map = RequestMap()
    request_map.bind(JoinMeetingCommand, JoinMeetingCommandHandler)

    mediator = Mediator(
        request_map=request_map,
        event_emitter=event_emitter,
        container=diska,
        middleware_chain=middleware_chain,
    )
    app.state.mediator = mediator
