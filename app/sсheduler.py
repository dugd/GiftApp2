from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.database import async_session
from app.service.event_service import generate_missing_occurrences


scheduler = AsyncIOScheduler(
    timezone="UTC",
    job_defaults={"max_instances": 1, "coalesce": True}
)


async def run_generate_occur() -> None:
    async with async_session() as db:
        created = await generate_missing_occurrences(db)
        print(f"[Scheduler] Generated new event occurrences: {created}")