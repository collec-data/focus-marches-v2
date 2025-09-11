from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./api/)
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    API_ROOT_PATH: str = "/api"
    DATABASE_URL: str = f"sqlite:///app/local.db"
    DEBUG: bool = False


config = Settings()  # type: ignore
