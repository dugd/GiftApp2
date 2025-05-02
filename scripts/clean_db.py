import os
import sys
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import text
from app.core.database import async_session
import app.api.v1.features.models # noqa
from app.models.base import Base


async def clean_tables():
    async with async_session() as db:
        for table in reversed(Base.metadata.sorted_tables):
            print(f'Truncating: {table.name}')
            await db.execute(text(f'TRUNCATE TABLE "{table.name}" RESTART IDENTITY CASCADE'))
        await db.commit()
        print("All tables truncated.")

def confirm() -> bool:
    answer = input("This will DELETE ALL DATA. Are you sure? (yes/no): ").strip().lower()
    return answer in {"yes", "y"}

def main():
    if not confirm():
        print("Aborted.")
        return
    asyncio.run(clean_tables())

if __name__ == "__main__":
    main()