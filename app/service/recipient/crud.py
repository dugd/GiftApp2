from uuid import UUID
from typing import Sequence

from app.service.recipient.policy import RecipientPolicy
from app.repositories.recipient import RecipientRepository
from app.models import Recipient, UserRole
from app.exceptions.exceptions import NotFoundError, PolicyPermissionError
from app.schemas.recipient import RecipientCreate, RecipientUpdateInfo, RecipientUpdateBirthday, RecipientModel
from app.schemas.user import UserModel


async def recipient_create(data: RecipientCreate, user: UserModel, repo: RecipientRepository) -> RecipientModel:
    if not RecipientPolicy(user).can_create():
        raise PolicyPermissionError("Forbidden to create recipient")
    recipient = Recipient(**data.model_dump(), user_id=user.id)
    await repo.add(recipient)
    await repo.commit()
    return RecipientModel.model_validate(recipient)


async def recipient_update_info(recipient_id: UUID, user: UserModel, data: RecipientUpdateInfo, repo: RecipientRepository) -> RecipientModel:
    recipient = await repo.get_by_id(recipient_id)
    if not RecipientPolicy(user).can_edit(RecipientModel.model_validate(recipient)):
        raise PolicyPermissionError("Forbidden to edit recipient")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(recipient, key, value)
    await repo.commit()
    return RecipientModel.model_validate(recipient)


async def recipient_update_birthday(recipient_id: UUID, user: UserModel, data: RecipientUpdateBirthday, repo: RecipientRepository) -> RecipientModel:
    recipient = await repo.get_by_id(recipient_id)
    if not RecipientPolicy(user).can_edit(RecipientModel.model_validate(recipient)):
        raise PolicyPermissionError("Forbidden to edit recipient")
    recipient.birthday = data.birthday
    await repo.commit()
    return RecipientModel.model_validate(recipient)


async def recipient_delete(recipient_id: UUID, user: UserModel, repo: RecipientRepository):
    recipient = await repo.get_by_id(recipient_id)
    if not RecipientPolicy(user).can_delete(RecipientModel.model_validate(recipient)):
        raise PolicyPermissionError("Forbidden to delete recipient")
    await repo.delete(recipient)
    await repo.commit()


async def get_recipient(recipient_id: UUID, user: UserModel, repo: RecipientRepository) -> RecipientModel:
    recipient = await repo.get_by_id(recipient_id)
    if not RecipientPolicy(user).can_view(RecipientModel.model_validate(recipient)):
        raise PolicyPermissionError("Forbidden to view recipient")
    if not recipient:
        raise NotFoundError("Recipient")
    return RecipientModel.model_validate(recipient)


async def get_recipient_list(user: UserModel, repo: RecipientRepository) -> Sequence[RecipientModel]:
    if user.role == UserRole.USER.value:
        recipients = await repo.get_by_user_id(user.id)
    else:
        recipients = await repo.get_all()
    return [RecipientModel.model_validate(recipient) for recipient in recipients]
