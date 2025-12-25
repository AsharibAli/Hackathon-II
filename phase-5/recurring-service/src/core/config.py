# [Task]: T003
# [Spec]: F-010 (R-010.1)
# [Description]: Recurring service configuration
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Recurring service configuration."""

    app_name: str = "recurring-service"
    app_version: str = "1.0.0"
    debug: bool = False

    # Dapr configuration
    dapr_http_port: int = 3500
    pubsub_name: str = "kafka-pubsub"

    # Backend API configuration
    backend_url: str = "http://localhost:8000"
    backend_timeout: int = 30

    # Logging
    log_level: str = "INFO"
    log_json: bool = True

    class Config:
        env_prefix = "RECURRING_"
        case_sensitive = False


settings = Settings()
