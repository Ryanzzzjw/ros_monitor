"""Application configuration via environment variables (prefix: RWM_)."""

from __future__ import annotations

import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = {"env_prefix": "RWM_"}

    # Server
    host: str = "0.0.0.0"
    port: int = 8080

    # ROS
    ros_node_name: str = "web_monitor"
    ros_domain_id: int | None = None

    # CORS
    cors_origins: list[str] = ["*"]

    # Polling
    node_poll_interval_sec: float = 2.0

    # WebSocket
    ws_max_message_rate: int = 30
    ws_queue_size: int = 50

    # Plugins
    enabled_plugins: list[str] = ["nodes", "topics"]

    def __init__(self, **kwargs: object) -> None:
        # Fall back to ROS_DOMAIN_ID env if RWM_ROS_DOMAIN_ID is not set
        if "ros_domain_id" not in kwargs and "RWM_ROS_DOMAIN_ID" not in os.environ:
            raw = os.environ.get("ROS_DOMAIN_ID")
            if raw is not None:
                kwargs["ros_domain_id"] = int(raw)
        super().__init__(**kwargs)


def get_settings() -> Settings:
    """Create and return application settings (singleton-friendly)."""
    return Settings()
