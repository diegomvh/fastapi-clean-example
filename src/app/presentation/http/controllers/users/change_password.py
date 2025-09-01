from inspect import getdoc
from typing import Annotated

from diator.mediator import Mediator
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Body, Path, Security, status
from fastapi_error_map import ErrorAwareRouter, rule

from app.application.common.exceptions.authorization import AuthorizationError
from app.application.features.user.commands.change_password import (
    ChangePasswordCommand,
    ChangePasswordCommandHandler,
)
from app.domain.exceptions.base import DomainFieldError
from app.domain.exceptions.user import UserNotFoundByUsernameError
from app.infrastructure.auth.exceptions import AuthenticationError
from app.infrastructure.exceptions.gateway import DataMapperError
from app.presentation.http.auth.fastapi_openapi_markers import cookie_scheme
from app.presentation.http.errors.callbacks import log_error, log_info
from app.presentation.http.errors.translators import (
    ServiceUnavailableTranslator,
)


def create_change_password_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.patch(
        "/{username}/password",
        description=getdoc(ChangePasswordCommandHandler),
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
        },
        default_on_error=log_info,
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Security(cookie_scheme)],
    )
    @inject
    async def change_password(
        username: Annotated[str, Path()],
        password: Annotated[str, Body()],
        mediator: FromDishka[Mediator],
    ) -> None:
        command = ChangePasswordCommand(
            username=username,
            password=password,
        )
        await mediator.send(command)

    return router
