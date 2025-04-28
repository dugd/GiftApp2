from fastapi import FastAPI

from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI()
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Welcome!", "app_name": settings.APP_NAME}
