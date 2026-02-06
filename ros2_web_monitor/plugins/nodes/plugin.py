"""Nodes plugin - monitors active ROS 2 nodes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter

from ros2_web_monitor.plugins.base import BasePlugin
from ros2_web_monitor.plugins.nodes.router import router

if TYPE_CHECKING:
    from fastapi import FastAPI

    from ros2_web_monitor.config import Settings


class NodesPlugin(BasePlugin):
    """Plugin that provides node listing and detail endpoints."""

    @property
    def name(self) -> str:
        return "nodes"

    @property
    def router(self) -> APIRouter:
        return router

    def startup(self, app: FastAPI, settings: Settings) -> None:
        """No additional startup needed — uses shared MonitorNode via DI."""

    def shutdown(self) -> None:
        """No resources to clean up."""
