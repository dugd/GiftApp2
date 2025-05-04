import os
import sys
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import text, Table
from app.core.database import async_session
import app.api.v1.features.models # noqa
from app.core.base import Base

def get_all_tables() -> list[Table]:
    return list(Base.metadata.sorted_tables)

def get_cascade_dependent_tables(selected_names: set[str]) -> set[str]:
    all_tables = {t.name: t for t in get_all_tables()}
    affected = set(selected_names)

    def add_dependents(target):
        for table in all_tables.values():
            for fk in table.foreign_key_constraints:
                if fk.referred_table.name == target and table.name not in affected:
                    affected.add(table.name)
                    add_dependents(table.name)

    for name in selected_names:
        add_dependents(name)

    return affected

async def truncate_selected_tables():
    async with async_session() as db:
        for table in reversed(Base.metadata.sorted_tables):
            print(f'Truncating: {table.name}')
            await db.execute(text(f'TRUNCATE TABLE "{table.name}" RESTART IDENTITY CASCADE'))
        await db.commit()
        print("All tables truncated.")

def select_tables() -> set[str]:
    all_tables = {t.name for t in get_all_tables()}

    print("\nAvailable tables:")
    for name in all_tables:
        print(f" - {name}")

    raw = input("\nEnter table names (comma-separated) or type 'all': ").strip().lower()
    if raw == "all":
        return all_tables

    selected = {name.strip() for name in raw.split(",") if name.strip() in all_tables}
    invalid = {name for name in raw.split(",") if name.strip() not in all_tables}
    if invalid:
        print(f"\nInvalid table(s): {', '.join(invalid)}")
        sys.exit(1)

    return selected

def confirm(target_tables: set[str], selected: set[str]) -> bool:
    print("\nTruncating the following selected tables:")
    for name in selected:
        print(f" - {name}")
    print("\nThis will also CASCADE to related tables:")
    cascade_only = target_tables - selected
    for name in cascade_only:
        print(f" - {name} (via FK)")

    answer = input("\nProceed with TRUNCATE CASCADE? (yes/no): ").strip().lower()
    return answer in {"yes", "y"}

def main():
    selected = select_tables()
    if not selected:
        print("No valid tables selected.")
        return

    target_tables = get_cascade_dependent_tables(selected)
    if not confirm(target_tables, selected):
        print("Aborted.")
        return
    asyncio.run(truncate_selected_tables())

if __name__ == "__main__":
    main()