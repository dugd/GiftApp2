from app.models import UserRole
from app.schemas.recipient import RecipientModel
from app.schemas.user import UserModel


class RecipientPolicy:
    def __init__(self, user: UserModel):
        self.user = user

    def _if_admin(self) -> bool:
        return self.user.role == UserRole.USER

    def _if_its_or_admin(self, recipient: RecipientModel):
        return recipient.user_id == self.user.id or self.user.role == UserRole.ADMIN


    def can_create(self):
        return self._if_admin()

    def can_view(self, recipient: RecipientModel):
        return self._if_its_or_admin(recipient)

    def can_edit(self, recipient: RecipientModel):
        return self._if_its_or_admin(recipient)

    def can_delete(self, recipient: RecipientModel):
        return self._if_its_or_admin(recipient)