import logging
from dataclasses import dataclass

from diator.events import Event
from diator.requests import Request, RequestHandler
from diator.response import Response

from app.application.common.exceptions.query import SortingError
from app.application.common.ports.user_query_gateway import UserQueryGateway
from app.application.common.query_models.user import UserQueryModel
from app.application.common.query_params.pagination import Pagination
from app.application.common.query_params.sorting import SortingOrder
from app.application.common.query_params.user import (
    UserListParams,
    UserListSorting,
)
from app.application.common.services.authorization.authorize import (
    authorize,
)
from app.application.common.services.authorization.permissions import (
    CanManageRole,
    RoleManagementContext,
)
from app.application.common.services.current_user import CurrentUserService
from app.domain.enums.user_role import UserRole

log = logging.getLogger(__name__)


@dataclass(kw_only=True)
class ListUsersQueryResponse(Response):
    """
    - Open to admins.
    - Retrieves a paginated list of existing users with relevant information.
    """

    users: list[UserQueryModel]


@dataclass(kw_only=True)
class ListUsersQueryRequest(Request[ListUsersQueryResponse]):
    """
    - Open to admins.
    - Retrieves a paginated list of existing users with relevant information.
    """

    limit: int
    offset: int
    sorting_field: str
    sorting_order: SortingOrder


class ListUsersQueryHandler(
    RequestHandler[ListUsersQueryRequest, ListUsersQueryResponse]
):
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

    async def handle(self, req: ListUsersQueryRequest) -> ListUsersQueryResponse:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        :raises ReaderError:
        :raises PaginationError:
        :raises SortingError:
        """
        log.info("List users: started.")

        current_user = await self._current_user_service.get_current_user()

        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject=current_user,
                target_role=UserRole.USER,
            ),
        )

        log.debug("Retrieving list of users.")
        user_list_params = UserListParams(
            pagination=Pagination(
                limit=req.limit,
                offset=req.offset,
            ),
            sorting=UserListSorting(
                sorting_field=req.sorting_field,
                sorting_order=req.sorting_order,
            ),
        )

        users: list[UserQueryModel] | None = await self._user_query_gateway.read_all(
            user_list_params,
        )
        if users is None:
            log.error(
                "Retrieving list of users failed: invalid sorting column '%s'.",
                req.sorting_field,
            )
            raise SortingError("Invalid sorting field.")

        response = ListUsersQueryResponse(users=users)

        log.info("List users: done.")
        return response
