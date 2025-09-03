from app.application.common.ports.access_revoker import AccessRevoker
from app.domain.value_objects.entity_id import EntityId
from app.infrastructure.auth.session.service import AuthSessionService


class AuthSessionAccessRevoker(AccessRevoker):
    def __init__(
        self,
        auth_session_service: AuthSessionService,
    ):
        self._auth_session_service = auth_session_service

    async def remove_all_user_access(self, user_id: EntityId) -> None:
        """
        :raises DataMapperError:
        """
        await self._auth_session_service.terminate_all_sessions_for_user(user_id)
