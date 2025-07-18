from uuid import UUID
from typing import Sequence, Optional

from app.service.recipient.policy import RecipientPolicy
from app.repositories.orm.recipient import RecipientRepository
from app.models import Recipient
from app.exceptions.common import NotFoundError, PolicyPermissionError
from app.schemas.recipient import RecipientCreate, RecipientUpdateInfo, RecipientUpdateBirthday, RecipientModel
from app.schemas.user import UserModel


class RecipientService:
    def __init__(self, repo: RecipientRepository, policy: type[RecipientPolicy]):
        self.repo = repo
        self.policy = policy

    async def _check_permission(self, user: UserModel, action: str, recipient: Recipient = None):
        policy = self.policy(user)
        schema = recipient and RecipientModel.model_validate(recipient)

        match action:
            case "create":
                allowed = policy.can_create()
            case "view":
                allowed = policy.can_view(schema)
            case "edit":
                allowed = policy.can_edit(schema)
            case "delete":
                allowed = policy.can_delete(schema)
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
        recipient = await self._get_model(recipient_id)
        await self._check_permission(user, "edit", recipient)
        updated = await self.repo.update(recipient, data.model_dump(exclude_unset=True))
        return RecipientModel.model_validate(updated)


    async def update_birthday(self, recipient_id: UUID, user: UserModel, data: RecipientUpdateBirthday) -> RecipientModel:
        recipient = await self._get_model(recipient_id)
        await self._check_permission(user, "edit", recipient)
        recipient.birthday = data.birthday
        updated = await self.repo.update(recipient, {})
        return RecipientModel.model_validate(updated)


    async def delete(self, recipient_id: UUID, user: UserModel):
        recipient = await self._get_model(recipient_id)
        await self._check_permission(user, "delete", recipient)
        await self.repo.delete(recipient)


    async def get_one(self, recipient_id: UUID, user: UserModel) -> RecipientModel:
        recipient = await self._get_model(recipient_id)
        await self._check_permission(user, "view", recipient)
        return RecipientModel.model_validate(recipient)


    async def list_my(
            self,
            user: UserModel,
            limit: int = 20,
            offset: int = 0,
            order_by: Optional[str] = None,
            desc_order: bool = False,
            filters: dict = None
    ) -> Sequence[RecipientModel]:
        filters = filters or {}
        recipients = await self.repo.get_by_user_id(
            user.id,
            limit=limit,
            skip=offset,
            order_by=order_by,
            desc_order=desc_order,
            **filters,
        )
        return [RecipientModel.model_validate(recipient) for recipient in recipients]

    async def _get_model(self, recipient_id: UUID) -> Recipient:
        recipient = await self.repo.get_by_id(recipient_id)
        if not recipient:
            raise NotFoundError("Recipient")
        return recipient
