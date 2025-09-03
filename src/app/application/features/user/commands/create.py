import logging
from dataclasses import dataclass
from uuid import UUID

from diator.requests import Request, RequestHandler
from diator.responses import Response

from app.application.common.ports.flusher import Flusher
from app.application.common.ports.uow import AsyncBaseUnitOfWork
from app.application.common.ports.user_command_gateway import UserCommandGateway
from app.application.common.services.authorization.authorize import (
    authorize,
)
from app.application.common.services.authorization.permissions import (
    CanManageRole,
    RoleManagementContext,
)
from app.application.common.services.current_user import CurrentUserService
from app.domain.enums.user_role import UserRole
from app.domain.exceptions.user import UsernameAlreadyExistsError
from app.domain.services.user import UserService
from app.domain.value_objects.raw_password.raw_password import RawPassword
from app.domain.value_objects.username.username import Username

log = logging.getLogger(__name__)


@dataclass(kw_only=True)
class CreateUserCommandResult(Response):
    id: UUID


@dataclass(kw_only=True)
class CreateUserCommand(Request[CreateUserCommandResult]):
    """
    - Open to admins.
    - Creates a new user, including admins, if the username is unique.
    - Only super admins can create new admins.
    """

    username: str
    password: str
    role: UserRole


class CreateUserCommandHandler(
    RequestHandler[CreateUserCommand, CreateUserCommandResult]
):
    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_service: UserService,
        user_command_gateway: UserCommandGateway,
        flusher: Flusher,
        uow: AsyncBaseUnitOfWork,
    ):
        super().__init__()
        self._current_user_service = current_user_service
        self._user_service = user_service
        self._user_command_gateway = user_command_gateway
        self._flusher = flusher
        self._uow = uow

    async def handle(self, req: CreateUserCommand) -> CreateUserCommandResult:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        :raises DomainFieldError:
        :raises RoleAssignmentNotPermittedError:
        :raises UsernameAlreadyExistsError:
        """
        log.info(
            "Create user: started. Username: '%s'.",
            req.username,
        )

        current_user = await self._current_user_service.get_current_user()

        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject=current_user,
                target_role=req.role,
            ),
        )

        username = Username(req.username)
        password = RawPassword(req.password)
        user = self._user_service.create_user(username, password, req.role)

        self._user_command_gateway.add(user)

        try:
            await self._flusher.flush()
        except UsernameAlreadyExistsError:
            raise

        await self._uow.commit()

        log.info("Create user: done. Username: '%s'.", user.username.value)
        return CreateUserCommandResult(id=user.id_.value)
