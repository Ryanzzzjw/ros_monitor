"""FastAPI dependency injection helpers."""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

from ros2_web_monitor.config import Settings

if TYPE_CHECKING:
    from ros2_web_monitor.ros_bridge.node import MonitorNode
    from ros2_web_monitor.ros_bridge.subscription_manager import SubscriptionManager

# Module-level references set during app startup
_monitor_node: MonitorNode | None = None
_subscription_manager: SubscriptionManager | None = None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()


def set_monitor_node(node: MonitorNode) -> None:
    """Store the monitor node reference (called during startup)."""
    global _monitor_node  # noqa: PLW0603
    _monitor_node = node


def get_monitor_node() -> MonitorNode:
    """FastAPI dependency: return the active MonitorNode."""
    if _monitor_node is None:
        from ros2_web_monitor.core.errors import ROSBridgeError
        raise ROSBridgeError("ROS bridge not initialized")
    return _monitor_node


def set_subscription_manager(manager: SubscriptionManager) -> None:
    """Store the subscription manager reference (called during startup)."""
    global _subscription_manager  # noqa: PLW0603
    _subscription_manager = manager


def get_subscription_manager() -> SubscriptionManager:
    """FastAPI dependency: return the active SubscriptionManager."""
    if _subscription_manager is None:
        from ros2_web_monitor.core.errors import ROSBridgeError
        raise ROSBridgeError("Subscription manager not initialized")
    return _subscription_manager
