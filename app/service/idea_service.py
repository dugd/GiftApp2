from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.exceptions import GiftAppError, NotFoundError
from app.models import GiftIdea, User, SimpleUser, AdminUser
from app.ideas.idea_schemas import IdeaCreate, IdeaModel, IdeaUpdateInfo


class IdeaService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_idea(self, data: IdeaCreate, user: User) -> IdeaModel:
        if isinstance(user, SimpleUser) and data.is_global:
            raise GiftAppError("forbidden")
        if isinstance(user, AdminUser) and not data.is_global:
            raise GiftAppError("must be global for admins")

        idea = GiftIdea(**data.model_dump(), user_id=user.id)
        self.db.add(idea)
        await self.db.commit()
        return IdeaModel.model_validate(idea)

    async def update_idea_info(self, idea_id: UUID, data: IdeaUpdateInfo, user: User) -> IdeaModel:
        idea = await self.get_idea_by_id(idea_id, user)
        if isinstance(user, SimpleUser):
            if idea.is_global:
                raise GiftAppError("forbidden to change global idea")
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(idea, key, value)
        await self.db.commit()
        return IdeaModel.model_validate(idea)

    async def soft_delete_idea(self, idea_id: UUID, user: User):
        idea = await self.get_idea_by_id(idea_id, user)
        if isinstance(user, SimpleUser):
            if idea.is_global:
                raise GiftAppError("forbidden to delete global idea")
        idea.soft_delete()
        await self.db.commit()

    async def archive_idea(self, idea_id: UUID, user: User) -> IdeaModel:
        idea = await self.get_idea_by_id(idea_id, user)
        if isinstance(user, SimpleUser):
            if idea.is_global:
                raise GiftAppError("forbidden to archive global idea")
        idea.archive()
        await self.db.commit()
        return IdeaModel.model_validate(idea)

    async def get_users_ideas_list(self, user_id: UUID) -> list[IdeaModel]:
        stmt = select(GiftIdea).where(GiftIdea.deleted_at == None).where(GiftIdea.user_id == user_id)
        result = await self.db.execute(stmt)
        ideas = result.scalars().all()
        return [IdeaModel.model_validate(idea) for idea in ideas]

    async def get_global_ideas_list(self) -> list[IdeaModel]:
        stmt = select(GiftIdea).where(GiftIdea.deleted_at == None).where(GiftIdea.is_global)
        result = await self.db.execute(stmt)
        ideas = result.scalars().all()
        return [IdeaModel.model_validate(idea) for idea in ideas]

    async def get_idea_by_id(self, idea_id: UUID, user: User) -> IdeaModel:
        stmt = select(GiftIdea).where(GiftIdea.deleted_at == None).where(GiftIdea.id == idea_id)
        result = await self.db.execute(stmt)
        idea = result.scalar_one_or_none()

        if not idea:
            raise NotFoundError("idea")
        if isinstance(user, SimpleUser):
            if idea.user_id != user.id:
                raise GiftAppError("forbidden to get idea")

        return IdeaModel.model_validate(idea)
