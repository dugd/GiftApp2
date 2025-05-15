from app.core.enums import UserRole
from app.schemas.user import UserModel
from app.schemas.idea import IdeaModel


class IdeaPolicy:
    def __init__(self, user: UserModel):
        self.user = user

    def _is_admin(self) -> bool:
        return self.user.role in {UserRole.ADMIN, UserRole.ROOT}

    @staticmethod
    def _is_global(idea: IdeaModel) -> bool:
        return idea.is_global

    def _is_its(self, idea: IdeaModel):
        return idea.user_id == self.user.id

    def can_create(self, is_global: bool):
        return self._is_admin() == is_global

    def can_view(self, idea: IdeaModel):
        return self._is_its(idea) or self._is_global(idea) or self._is_admin()

    def can_edit(self, idea: IdeaModel):
        return self._is_its(idea) or self._is_admin()

    def can_delete(self, idea: IdeaModel):
        return self._is_its(idea) or self._is_admin()