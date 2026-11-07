from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SPREADSHEET_ID: str
    GOOGLE_CREDENTIALS_PATH: str = "credentials.json"
    APP_NAME: str = "MaidPad Lead Automation"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()