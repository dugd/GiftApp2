from uuid import UUID
from typing import Sequence

from app.service.recipient.policy import RecipientPolicy
from app.repositories.orm.recipient import RecipientRepository
from app.models import Recipient
from app.core.enums import UserRole
from app.exceptions.common import NotFoundError, PolicyPermissionError
from app.schemas.recipient import RecipientCreate, RecipientUpdateInfo, RecipientUpdateBirthday, RecipientModel
from app.schemas.user import UserModel


class RecipientService:
    def __init__(self, repo: RecipientRepository, policy: type[RecipientPolicy]):
        self.repo = repo
        self.policy = policy

    async def _check_permission(self, user: UserModel, action: str, recipient: RecipientModel = None):
        policy = self.policy(user)

        match action:
            case "create":
                allowed = policy.can_create()
            case "view":
                allowed = policy.can_view(recipient)
            case "edit":
                allowed = policy.can_edit(recipient)
            case "delete":
                allowed = policy.can_delete(recipient)
            case _:
                raise ValueError(f"Unknown action '{action}'")

        if not allowed:
            raise PolicyPermissionError(f"Forbidden to {action} recipient")

    async def create(self, user: UserModel, data: RecipientCreate) -> RecipientModel:
        await self._check_permission(user, "create")
        recipient = Recipient(**data.model_dump(), user_id=user.id)
        await self.repo.add(recipient)
        return RecipientModel.model_validate(recipient)

    async def update_info(self, recipient_id: UUID, user: UserModel, data: RecipientUpdateInfo) -> RecipientModel:
        recipient = await self.repo.get_by_id(recipient_id)
        await self._check_permission(user, "edit", recipient)
        updated = await self.repo.update(recipient, data.model_dump(exclude_unset=True))
        return RecipientModel.model_validate(updated)


    async def update_birthday(self, recipient_id: UUID, user: UserModel, data: RecipientUpdateBirthday) -> RecipientModel:
        recipient = await self.repo.get_by_id(recipient_id)
        await self._check_permission(user, "edit", recipient)
        recipient.birthday = data.birthday
        updated = await self.repo.update(recipient, {})
        return RecipientModel.model_validate(updated)


    async def delete(self, recipient_id: UUID, user: UserModel):
        recipient = await self.repo.get_by_id(recipient_id)
        await self._check_permission(user, "delete", recipient)
        await self.repo.delete(recipient)


    async def get_recipient(self, recipient_id: UUID, user: UserModel) -> RecipientModel:
        recipient = await self.repo.get_by_id(recipient_id)
        if not recipient:
            raise NotFoundError("Recipient")
        await self._check_permission(user, "view", recipient)
        return RecipientModel.model_validate(recipient)


    async def list(self, user: UserModel) -> Sequence[RecipientModel]:
        if user.role == UserRole.USER.value:
            recipients = await self.repo.get_by_user_id(user.id)
        else:
            recipients = await self.repo.list()
        return [RecipientModel.model_validate(recipient) for recipient in recipients]
