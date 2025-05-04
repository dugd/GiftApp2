from contextlib import asynccontextmanager

from fastapi import FastAPI
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.sсheduler import scheduler, run_generate_occur
from app.api.v1.router import api_router

@asynccontextmanager
async def lifespan(_: FastAPI):
    print("Starting APScheduler...")
    scheduler.add_job(
        run_generate_occur,
        CronTrigger(hour=0, minute=0),
        id='generate_missing_occurrences',
        replace_existing=True,
    )
    scheduler.start()
    yield
    print("Shutdown APScheduler...")
    scheduler.shutdown(wait=False)


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Welcome!", "app_name": settings.APP_NAME}
