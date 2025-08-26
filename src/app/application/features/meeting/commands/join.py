from dataclasses import dataclass, field

from diator.events import Event
from diator.requests import Request, RequestHandler

from app.application.common.ports.user_query_gateway import UserQueryGateway
from app.application.common.services.current_user import CurrentUserService


@dataclass(frozen=True, kw_only=True)
class JoinMeetingCommand(Request):
    meeting_id: int
    user_id: int
    is_late: bool = field(default=False)


class JoinMeetingCommandHandler(RequestHandler[JoinMeetingCommand, None]):
    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_query_gateway: UserQueryGateway,
    ):
        self._current_user_service = current_user_service
        self._user_query_gateway = user_query_gateway
        self._events: list[Event] = []

    @property
    def events(self) -> list[Event]:
        return self._events

    async def handle(self, request: JoinMeetingCommand) -> None:
        pass
