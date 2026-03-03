"""Background thread executor for rclpy spin loop."""

from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING

import rclpy
from rclpy.executors import SingleThreadedExecutor

if TYPE_CHECKING:
    from rclpy.context import Context
    from rclpy.node import Node

logger = logging.getLogger(__name__)


class ROSExecutor:
    """Manages rclpy lifecycle and spins nodes in a background thread.

    Main thread: asyncio event loop (FastAPI/uvicorn)
    Background thread: rclpy SingleThreadedExecutor.spin()
    """

    def __init__(self, *, context: Context | None = None) -> None:
        self._executor: SingleThreadedExecutor | None = None
        self._thread: threading.Thread | None = None
        self._shutdown_event = threading.Event()
        self._context = context

    def start(self, nodes: list[Node]) -> None:
        """Initialize rclpy, add nodes, and start the spin thread."""
        self._shutdown_event.clear()
        self._executor = SingleThreadedExecutor(context=self._context)
        for node in nodes:
            self._executor.add_node(node)

        self._thread = threading.Thread(
            target=self._spin_loop,
            name="ros-executor",
            daemon=True,
        )
        self._thread.start()
        logger.info("ROS executor started in background thread")

    def _spin_loop(self) -> None:
        """Spin the executor until shutdown is requested."""
        assert self._executor is not None
        try:
            while not self._shutdown_event.is_set():
                self._executor.spin_once(timeout_sec=0.1)
        except Exception:
            logger.exception("ROS executor spin loop crashed")
        finally:
            logger.info("ROS executor spin loop exited")

    def shutdown(self) -> None:
        """Stop the spin loop, join the thread, and shut down rclpy."""
        logger.info("Shutting down ROS executor...")
        self._shutdown_event.set()

        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=5.0)
            if self._thread.is_alive():
                logger.warning("ROS executor thread did not exit cleanly")

        if self._executor is not None:
            self._executor.shutdown()
            self._executor = None

        if self._context is not None and self._context.ok():
            self._context.shutdown()
        elif rclpy.ok():
            rclpy.shutdown()

        logger.info("ROS executor shutdown complete")
