"""Plugin auto-discovery and registration."""

from __future__ import annotations

import importlib
import logging
from typing import TYPE_CHECKING

from ros2_web_monitor.core.errors import PluginError
from ros2_web_monitor.plugins.base import BasePlugin

if TYPE_CHECKING:
    from fastapi import FastAPI

    from ros2_web_monitor.config import Settings

logger = logging.getLogger(__name__)


class PluginRegistry:
    """Discovers, loads, and manages plugin lifecycle."""

    def __init__(self) -> None:
        self._plugins: dict[str, BasePlugin] = {}

    @property
    def plugins(self) -> dict[str, BasePlugin]:
        """Return all registered plugins."""
        return dict(self._plugins)

    def discover_and_register(self, enabled_plugins: list[str]) -> None:
        """Discover and instantiate plugins from the enabled list.

        Each plugin is expected at: ros2_web_monitor.plugins.<name>.plugin
        with a class that subclasses BasePlugin.
        """
        for plugin_name in enabled_plugins:
            module_path = f"ros2_web_monitor.plugins.{plugin_name}.plugin"
            try:
                module = importlib.import_module(module_path)
            except ImportError as exc:
                raise PluginError(f"Cannot import plugin '{plugin_name}': {exc}") from exc

            # Find the BasePlugin subclass in the module
            plugin_cls = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, BasePlugin)
                    and attr is not BasePlugin
                ):
                    plugin_cls = attr
                    break

            if plugin_cls is None:
                raise PluginError(
                    f"No BasePlugin subclass found in '{module_path}'"
                )

            plugin = plugin_cls()
            if plugin.name != plugin_name:
                raise PluginError(
                    f"Plugin name mismatch: expected '{plugin_name}', got '{plugin.name}'"
                )

            self._plugins[plugin_name] = plugin
            logger.info("Registered plugin: %s", plugin_name)

    def startup_all(self, app: FastAPI, settings: Settings) -> None:
        """Call startup() on all registered plugins and mount their routers."""
        for name, plugin in self._plugins.items():
            plugin.startup(app, settings)
            app.include_router(plugin.router)
            logger.info("Plugin '%s' started and router mounted", name)

    def shutdown_all(self) -> None:
        """Call shutdown() on all registered plugins."""
        for name, plugin in self._plugins.items():
            try:
                plugin.shutdown()
                logger.info("Plugin '%s' shut down", name)
            except Exception:
                logger.exception("Error shutting down plugin '%s'", name)
