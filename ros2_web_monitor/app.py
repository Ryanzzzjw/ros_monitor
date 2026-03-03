"""FastAPI application factory."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rclpy.context import Context

from ros2_web_monitor.config import Settings
from ros2_web_monitor.core.dependencies import (
    set_monitor_node,
    set_subscription_manager,
)
from ros2_web_monitor.core.middleware import ErrorHandlerMiddleware, RequestLoggingMiddleware
from ros2_web_monitor.plugins.registry import PluginRegistry
from ros2_web_monitor.ros_bridge.executor import ROSExecutor
from ros2_web_monitor.ros_bridge.node import MonitorNode
from ros2_web_monitor.ros_bridge.subscription_manager import SubscriptionManager

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    if settings is None:
        settings = Settings()

    # Shared state created here, stored in app.state for lifecycle management
    plugin_registry = PluginRegistry()
    ros_executor: ROSExecutor | None = None
    sub_manager: SubscriptionManager | None = None

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        """Manage application lifecycle: startup and shutdown."""
        nonlocal ros_executor, sub_manager

        # --- Startup ---
        logger.info("Starting ROS 2 Web Monitor...")

        # 1. Create isolated ROS context for this app lifecycle
        ros_context = Context()
        if settings.ros_domain_id is None:
            ros_context.init(args=None)
        else:
            ros_context.init(args=None, domain_id=settings.ros_domain_id)

        # 2. Create MonitorNode
        monitor_node = MonitorNode(
            settings.ros_node_name,
            context=ros_context,
            domain_id=settings.ros_domain_id,
        )

        # 3. Start ROS executor in background thread
        ros_executor = ROSExecutor(context=ros_context)
        ros_executor.start([monitor_node])

        # 4. Create SubscriptionManager (needs asyncio event loop)
        loop = asyncio.get_running_loop()
        sub_manager = SubscriptionManager(
            monitor_node,
            loop,
            queue_size=settings.ws_queue_size,
        )

        # 5. Register dependencies for DI
        set_monitor_node(monitor_node)
        set_subscription_manager(sub_manager)

        # 6. Discover and start plugins
        plugin_registry.discover_and_register(settings.enabled_plugins)
        plugin_registry.startup_all(app, settings)

        logger.info("ROS 2 Web Monitor started successfully")
        yield

        # --- Shutdown (graceful sequence per CLAUDE.md) ---
        logger.info("Shutting down ROS 2 Web Monitor...")

        # 1. Shut down plugins (stops accepting new connections)
        plugin_registry.shutdown_all()

        # 2. Destroy all rclpy subscriptions
        if sub_manager is not None:
            sub_manager.shutdown()

        # 3. Stop executor spin loop and join background thread
        if ros_executor is not None:
            ros_executor.shutdown()

        logger.info("ROS 2 Web Monitor shutdown complete")

    app = FastAPI(
        title="ROS 2 Web Monitor",
        version="0.1.0",
        lifespan=lifespan,
    )

    # --- Middleware (order matters: last added = first executed) ---
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(ErrorHandlerMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Health check ---
    @app.get("/api/v1/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    # --- Config endpoint (expose non-sensitive settings to frontend) ---
    @app.get("/api/v1/config")
    async def config() -> dict[str, object]:
        return {
            "domain_id": settings.ros_domain_id,
            "node_name": settings.ros_node_name,
        }

    return app
