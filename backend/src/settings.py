from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://reposalud:reposalud@localhost:5432/reposalud"
    upload_dir: Path = Path("./uploads")
    jwt_secret: str = "dev-secret-change-me"
    # Seconds; env var is JWT_EXPIRATION per the activity spec. Default matches the
    # contract's documented session lifetime (RNF-06): 30 days.
    jwt_expiration: int = 2_592_000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
