from inspect import getdoc
from typing import Annotated

from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Path, Request, Security, status
from fastapi_error_map import ErrorAwareRouter, rule

from app.application.common.exceptions.authorization import AuthorizationError
from app.application.features.meeting.commands.join import (
    JoinMeetingCommand,
)
from app.domain.exceptions.base import DomainFieldError
from app.domain.exceptions.user import (
    ActivationChangeNotPermittedError,
    UserNotFoundByUsernameError,
)
from app.infrastructure.auth.exceptions import AuthenticationError
from app.infrastructure.exceptions.gateway import DataMapperError
from app.presentation.http.auth.fastapi_openapi_markers import cookie_scheme
from app.presentation.http.errors.callbacks import log_error, log_info
from app.presentation.http.errors.translators import ServiceUnavailableTranslator


def create_join_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.get(
        "/{meeting_id}/{user_id}/join",
        description=getdoc(JoinMeetingCommand),
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            UserNotFoundByUsernameError: status.HTTP_404_NOT_FOUND,
            ActivationChangeNotPermittedError: status.HTTP_403_FORBIDDEN,
        },
        default_on_error=log_info,
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Security(cookie_scheme)],
    )
    @inject
    async def join_meeting(
        meeting_id: Annotated[int, Path()],
        user_id: Annotated[int, Path()],
        request: Request,
    ) -> None:
        command = JoinMeetingCommand(meeting_id=meeting_id, user_id=user_id)
        await request.app.state.mediator.send(command)

    return router


def create_meetings_router() -> APIRouter:
    router = APIRouter(
        prefix="/meetings",
        tags=["Meetings"],
    )

    sub_routers = (create_join_router(),)

    for sub_router in sub_routers:
        router.include_router(sub_router)

    return router
