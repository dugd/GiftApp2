from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from apscheduler.triggers.cron import CronTrigger
from starlette.responses import JSONResponse

from app.core.config import settings
from app.sсheduler import scheduler, run_generate_occur
from app.api.v1.router import api_router
from app.exceptions import GiftAppError

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


@app.exception_handler(GiftAppError)
async def app_exception_handler(_: Request, exc: GiftAppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )

app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Welcome!", "app_name": settings.APP_NAME}
