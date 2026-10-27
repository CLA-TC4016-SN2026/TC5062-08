from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://reposalud:reposalud@localhost:5432/reposalud"
    upload_dir: Path = Path("./uploads")
    jwt_secret: str = "dev-secret-change-me"
    # Seconds; env var is JWT_EXPIRATION per the activity spec. Default matches the
    # contract's documented session lifetime (RNF-06): 30 days. Bounded so a
    # misconfigured value can't produce a token that (effectively) never expires.
    jwt_expiration: int = Field(default=2_592_000, ge=60, le=365 * 24 * 3600)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("jwt_secret")
    @classmethod
    def _jwt_secret_must_be_strong(cls, value: str) -> str:
        if len(value) < 32:
            raise ValueError(
                "JWT_SECRET debe tener al menos 32 caracteres (genera uno con "
                "python -c \"import secrets; print(secrets.token_urlsafe(48))\")."
            )
        return value


settings = Settings()
