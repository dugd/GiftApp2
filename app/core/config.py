from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "My App"
    DEBUG: bool = False

    DATABASE_URL: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ACTIVATION_TOKEN_EXPIRE_HOURS: int = 24

    AWS_ACCESS_KEY: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "eu-central-1"
    AWS_BUCKET_NAME: str

    MAIL_ENABLED: bool = False
    MAIL_SENDGRID_API_KEY: str
    MAIL_SENDER_EMAIL: str


@lru_cache
def get_settings():
    settings = Settings()
    return settings
