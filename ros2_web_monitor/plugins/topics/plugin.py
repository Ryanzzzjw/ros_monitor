"""Topics plugin - monitors ROS 2 topics with real-time WebSocket streaming."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter

from ros2_web_monitor.plugins.base import BasePlugin
from ros2_web_monitor.plugins.topics.router import router

if TYPE_CHECKING:
    from fastapi import FastAPI

    from ros2_web_monitor.config import Settings


class TopicsPlugin(BasePlugin):
    """Plugin that provides topic listing, detail, stats, and WebSocket streaming."""

    @property
    def name(self) -> str:
        return "topics"

    @property
    def router(self) -> APIRouter:
        return router

    def startup(self, app: FastAPI, settings: Settings) -> None:
        """No additional startup needed — uses shared MonitorNode and SubscriptionManager via DI."""

    def shutdown(self) -> None:
        """No resources to clean up — SubscriptionManager handles subscription lifecycle."""
