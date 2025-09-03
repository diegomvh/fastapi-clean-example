from dishka import Provider, Scope, provide, provide_all

from app.application.common.ports.access_revoker import AccessRevoker
from app.application.common.ports.flusher import Flusher
from app.application.common.ports.identity_provider import IdentityProvider
from app.application.common.ports.uow import AsyncBaseUnitOfWork
from app.application.common.ports.user_command_gateway import UserCommandGateway
from app.application.common.ports.user_query_gateway import UserQueryGateway
from app.application.common.services.current_user import CurrentUserService
from app.application.features.user.commands.activate import ActivateUserCommandHandler
from app.application.features.user.commands.change_password import (
    ChangePasswordCommandHandler,
)
from app.application.features.user.commands.create import CreateUserCommandHandler
from app.application.features.user.commands.deactivate import (
    DeactivateUserCommandHandler,
)
from app.application.features.user.commands.grant_admin import GrantAdminCommandHandler
from app.application.features.user.commands.revoke_admin import (
    RevokeAdminCommandHandler,
)
from app.application.features.user.queries.list import ListUsersQueryHandler
from app.infrastructure.adapters.main_flusher_sqla import SqlaMainFlusher
from app.infrastructure.adapters.uow import AsyncSQLAlchemyUnitOfWork
from app.infrastructure.adapters.user_data_mapper_sqla import (
    SqlaUserDataMapper,
)
from app.infrastructure.adapters.user_reader_sqla import SqlaUserReader
from app.infrastructure.auth.adapters.access_revoker import (
    AuthSessionAccessRevoker,
)
from app.infrastructure.auth.adapters.identity_provider import (
    AuthSessionIdentityProvider,
)


class ApplicationProvider(Provider):
    scope = Scope.REQUEST

    # Services
    services = provide_all(
        CurrentUserService,
    )

    # Ports Auth
    access_revoker = provide(
        source=AuthSessionAccessRevoker,
        provides=AccessRevoker,
    )
    identity_provider = provide(
        source=AuthSessionIdentityProvider,
        provides=IdentityProvider,
    )

    # Ports Persistence
    uow = provide(
        source=AsyncSQLAlchemyUnitOfWork,
        provides=AsyncBaseUnitOfWork,
    )
    flusher = provide(
        source=SqlaMainFlusher,
        provides=Flusher,
    )
    user_command_gateway = provide(
        source=SqlaUserDataMapper,
        provides=UserCommandGateway,
    )
    user_query_gateway = provide(
        source=SqlaUserReader,
        provides=UserQueryGateway,
    )

    # Commands
    commands = provide_all(
        ActivateUserCommandHandler,
        ChangePasswordCommandHandler,
        CreateUserCommandHandler,
        DeactivateUserCommandHandler,
        GrantAdminCommandHandler,
        RevokeAdminCommandHandler,
    )

    # Queries
    queries = provide_all(
        ListUsersQueryHandler,
    )
