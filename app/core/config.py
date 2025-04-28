from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    APP_NAME: str = "My App"
    DEBUG: bool = False

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

settings = Settings()