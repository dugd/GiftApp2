from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import get_settings

settings = get_settings()


DATABASE_URL = settings.DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_async_engine(DATABASE_URL, echo=settings.DEBUG)
async_session = async_sessionmaker(engine, expire_on_commit=False)
