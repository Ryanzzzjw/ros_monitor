"""Base plugin abstract class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import APIRouter, FastAPI

    from ros2_web_monitor.config import Settings


class BasePlugin(ABC):
    """Abstract base class for all ROS Web Monitor plugins.

    Each plugin is self-contained with its own router, schemas, and service.
    Plugins are discovered and registered automatically by the plugin registry.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique plugin identifier (matches directory name)."""

    @property
    @abstractmethod
    def router(self) -> APIRouter:
        """FastAPI router with the plugin's endpoints."""

    @abstractmethod
    def startup(self, app: FastAPI, settings: Settings) -> None:
        """Called during application startup. Initialize resources here."""

    @abstractmethod
    def shutdown(self) -> None:
        """Called during application shutdown. Clean up resources here."""
