import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import select

from app.core.database import async_session
from app.api.v1.features.recipients.models import Recipient # noqa
from app.api.v1.features.auth.models import RootUser
from app.api.v1.features.auth.security import hash_password


async def create_root():
    user_email = "root@example.com"
    password = "12345678"
    async with async_session() as db:
        stmt = select(RootUser).where(RootUser.email == user_email)
        result = await db.execute(stmt)
        existing_root = result.scalar_one_or_none()
        if existing_root:
            print("Root user already exists.")
            return
        root = RootUser(
            email=user_email,
            hashed_password=hash_password(password),
        )
        db.add(root)
        await db.commit()
        print("Root user created.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(create_root())