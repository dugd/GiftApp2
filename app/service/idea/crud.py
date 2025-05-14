from uuid import UUID
from typing import Sequence

from app.repositories.orm import IdeaRepository
from app.schemas.idea import IdeaCreate, IdeaUpdateInfo, IdeaModel
from app.schemas.user import UserModel
from app.exceptions.common import NotFoundError, PolicyPermissionError
from app.service.idea.policy import IdeaPolicy
from app.models import GiftIdea


class IdeaService:
    def __init__(self, repo: IdeaRepository, policy_cls: type[IdeaPolicy]):
        self.repo = repo
        self.policy_cls = policy_cls

    def _check_permission(self, user: UserModel, action: str, idea: GiftIdea = None, is_global: bool = False):
        policy = self.policy_cls(user)
        schema = idea and IdeaModel.model_validate(idea)

        match action:
            case "create":
                allowed = policy.can_create(is_global)
            case "view":
                allowed = policy.can_view(schema)
            case "edit":
                allowed = policy.can_edit(schema)
            case "delete":
                allowed = policy.can_delete(schema)
            case _:
                raise ValueError(f"Unknown policy action: {action}")

        if not allowed:
            raise PolicyPermissionError(f"Forbidden to {action} idea")

    async def create(self, user: UserModel, data: IdeaCreate) -> IdeaModel:
        self._check_permission(user, "create", is_global=data.is_global)
        idea = GiftIdea(**data.model_dump(), user_id=user.id)
        await self.repo.add(idea)
        return IdeaModel.model_validate(idea)

    async def update_info(self, user: UserModel, idea_id: UUID, data: IdeaUpdateInfo) -> IdeaModel:
        idea = await self._get_model(idea_id)
        self._check_permission(user, "edit", idea)
        updated = await self.repo.update(idea, data.model_dump(exclude_unset=True))
        return IdeaModel.model_validate(updated)

    async def soft_delete(self, user: UserModel, idea_id: UUID):
        idea = await self._get_model(idea_id)
        self._check_permission(user, "delete", idea)
        idea.soft_delete()
        await self.repo.update(idea, {})

    async def archive(self, user: UserModel, idea_id: UUID) -> IdeaModel:
        idea = await self._get_model(idea_id)
        self._check_permission(user, "edit", idea)
        idea.archive()
        updated = await self.repo.update(idea, {})
        return IdeaModel.model_validate(updated)

    async def get_user_ideas(self, user: UserModel) -> Sequence[IdeaModel]:
        ideas = await self.repo.get_by_user_id(user.id)
        return [IdeaModel.model_validate(i) for i in ideas]

    async def get_global_ideas(self) -> Sequence[IdeaModel]:
        ideas = await self.repo.list(is_global=True)
        return [IdeaModel.model_validate(i) for i in ideas]

    async def get_one(self, user: UserModel, idea_id: UUID) -> IdeaModel:
        idea = await self._get_model(idea_id)
        self._check_permission(user, "view", idea)
        return IdeaModel.model_validate(idea)

    async def _get_model(self, idea_id: UUID) -> GiftIdea:
        idea = await self.repo.get_by_id(idea_id)
        if not idea:
            raise NotFoundError("Idea")
        return idea
