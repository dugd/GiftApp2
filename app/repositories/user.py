from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.orm import SQLAlchemyRepository
from app.models import User


class UserRepository(SQLAlchemyRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(self._model).where(self._model.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
