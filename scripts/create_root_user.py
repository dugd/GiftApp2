import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import select

from app.core.database import async_session
from app.api.v1.features.models import RootUser # noqa
from app.api.v1.features.auth.security import hash_password


DEFAULT_ROOT_EMAIL = "root@example.com"
DEFAULT_ROOT_PASSWORD = "12345678"


async def create_root(root_email: str, root_password: str):
    async with async_session() as db:
        stmt = select(RootUser).where(RootUser.email == root_email)
        result = await db.execute(stmt)
        existing_root = result.scalar_one_or_none()
        if existing_root:
            print("Root user already exists.")
            return
        root = RootUser(
            email=root_email,
            hashed_password=hash_password(root_password),
        )
        db.add(root)
        await db.commit()
        print("Root user created.")


def main():
    import asyncio

    arg_email = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ROOT_EMAIL
    arg_password = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_ROOT_PASSWORD

    asyncio.run(create_root(arg_email, arg_password))


if __name__ == "__main__":
    main()