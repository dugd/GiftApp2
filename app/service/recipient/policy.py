# app/service/recipient/policy.py
from app.schemas.recipient import RecipientModel
from app.schemas.user import UserModel
from app.core.enums import UserRole


class RecipientPolicy:
    def __init__(self, user: UserModel):
        self.user = user

    def _is_admin(self) -> bool:
        return self.user.role in {UserRole.ADMIN, UserRole.ROOT}

    def _is_owner(self, recipient: RecipientModel) -> bool:
        return recipient.user_id == self.user.id

    def can_create(self) -> bool:
        return self.user.role == UserRole.USER

    def can_view(self, recipient: RecipientModel) -> bool:
        return self._is_owner(recipient) or self._is_admin()

    def can_edit(self, recipient: RecipientModel) -> bool:
        return self._is_owner(recipient) or self._is_admin()

    def can_delete(self, recipient: RecipientModel) -> bool:
        return self._is_owner(recipient) or self._is_admin()
