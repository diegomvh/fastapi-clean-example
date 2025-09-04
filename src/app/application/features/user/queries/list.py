import logging
from dataclasses import dataclass

from diator.requests import Request, RequestHandler
from diator.responses import Response

from app.application.common.exceptions.query import SortingError
from app.application.common.ports.uow import AsyncBaseUnitOfWork
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
from app.domain.entities.user import User
from app.domain.enums.user_role import UserRole

log = logging.getLogger(__name__)


@dataclass(kw_only=True)
class ListUsersQueryResult(Response):
    """
    - Open to admins.
    - Retrieves a paginated list of existing users with relevant information.
    """

    users: list[UserQueryModel]


@dataclass(kw_only=True)
class ListUsersQuery(Request[ListUsersQueryResult]):
    """
    - Open to admins.
    - Retrieves a paginated list of existing users with relevant information.
    """

    limit: int
    offset: int
    sorting_field: str
    sorting_order: SortingOrder


class ListUsersQueryHandler(RequestHandler[ListUsersQuery, ListUsersQueryResult]):
    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_query_gateway: UserQueryGateway,
        uow: AsyncBaseUnitOfWork,
    ):
        super().__init__()
        self._current_user_service = current_user_service
        self._user_query_gateway = user_query_gateway
        self._uow = uow

    async def handle(self, req: ListUsersQuery) -> ListUsersQueryResult:
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

        user_repository = self._uow.repository(User)
        all_users = await user_repository.all(
            username="diego",
        )
        print(all_users)  # noqa: T201

        users: list[UserQueryModel] | None = await self._user_query_gateway.read_all(
            user_list_params,
        )
        if users is None:
            log.error(
                "Retrieving list of users failed: invalid sorting column '%s'.",
                req.sorting_field,
            )
            raise SortingError("Invalid sorting field.")

        response = ListUsersQueryResult(users=users)

        log.info("List users: done.")
        return response
