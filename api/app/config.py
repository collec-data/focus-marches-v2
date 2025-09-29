from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./api/)
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    DATABASE_URL: str
    DEBUG: bool = False

    API_ENTREPRISE_URL: str
    API_ENTREPRISE_TOKEN: str


@lru_cache
def get_config() -> Config:
    return Config()  # type: ignore
