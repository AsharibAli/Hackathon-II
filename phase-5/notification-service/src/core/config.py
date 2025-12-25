# [Task]: T002
# [Spec]: F-009 (R-009.1)
# [Description]: Notification service configuration
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Notification service configuration."""

    app_name: str = "notification-service"
    app_version: str = "1.0.0"
    debug: bool = False

    # Dapr configuration
    dapr_http_port: int = 3500
    pubsub_name: str = "kafka-pubsub"

    # Logging
    log_level: str = "INFO"
    log_json: bool = True

    class Config:
        env_prefix = "NOTIFICATION_"
        case_sensitive = False


settings = Settings()
