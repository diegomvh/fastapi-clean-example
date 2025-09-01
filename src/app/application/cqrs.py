from diator.events import EventMap
from diator.requests import RequestMap

from app.application.features.user.commands import (
    ChangePasswordCommand,
    ChangePasswordCommandHandler,
    CreateUserCommand,
    CreateUserCommandHandler,
    DeactivateUserCommand,
    DeactivateUserCommandHandler,
    GrantAdminCommand,
    GrantAdminCommandHandler,
    RevokeAdminCommand,
    RevokeAdminCommandHandler,
)
from app.application.features.user.queries import (
    ListUsersQuery,
    ListUsersQueryHandler,
)

# Requests
request_map = RequestMap()

# Commands
request_map.bind(CreateUserCommand, CreateUserCommandHandler)
request_map.bind(ChangePasswordCommand, ChangePasswordCommandHandler)
request_map.bind(DeactivateUserCommand, DeactivateUserCommandHandler)
request_map.bind(GrantAdminCommand, GrantAdminCommandHandler)
request_map.bind(RevokeAdminCommand, RevokeAdminCommandHandler)

# Queries
request_map.bind(ListUsersQuery, ListUsersQueryHandler)

# Events
event_map = EventMap()
