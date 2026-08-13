from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables (see .env.example)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./visa_application.db"
    audit_database_url: str = "sqlite:///./visa_application_audit.db"
    integrations_mocked: bool = True
    identity_provider_jwt_secret: str = "dev-only-not-a-real-secret"
    notification_gateway_api_key: str = "dev-only-not-a-real-secret"
    environment: str = "scaffold"


@lru_cache
def get_settings() -> Settings:
    return Settings()
