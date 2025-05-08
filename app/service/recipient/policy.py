from app.models import UserRole
from app.schemas.recipient import RecipientModel
from app.schemas.user import UserModel


class RecipientPolicy:
    def __init__(self, user: UserModel):
        self.user = user

    def _is_admin(self) -> bool:
        return self.user.role == UserRole.USER

    def _is_its(self, recipient: RecipientModel):
        return recipient.user_id == self.user.id

    def can_create(self):
        return not self._is_admin()

    def can_view(self, recipient: RecipientModel):
        return self._is_its(recipient) or self._is_admin()

    def can_edit(self, recipient: RecipientModel):
        return self._is_its(recipient) or self._is_admin()

    def can_delete(self, recipient: RecipientModel):
        return self._is_its(recipient) or self._is_admin()