"""MonitorNode - ROS 2 node for graph introspection."""

from __future__ import annotations

import logging
import threading
from typing import Any

from rclpy.node import Node

logger = logging.getLogger(__name__)


class MonitorNode(Node):
    """ROS 2 node that provides graph introspection capabilities.

    This node runs in the background rclpy executor thread.
    All graph query methods are thread-safe for calling from the asyncio thread,
    as rclpy graph introspection APIs are read-only and internally synchronized
    on supported distros (Humble/Jazzy).
    """

    def __init__(self, node_name: str, *, domain_id: int | None = None) -> None:
        kwargs: dict[str, Any] = {}
        if domain_id is not None:
            from rclpy.context import Context
            ctx = Context()
            ctx.init(args=None, domain_id=domain_id)
            kwargs["context"] = ctx

        super().__init__(node_name, **kwargs)
        self._lock = threading.Lock()
        logger.info("MonitorNode '%s' created (domain_id=%s)", node_name, domain_id)

    def get_node_names_with_namespaces(self) -> list[tuple[str, str]]:
        """Return list of (node_name, namespace) tuples for all discovered nodes."""
        names_and_ns = super().get_node_names_and_namespaces()
        return [(name, ns) for name, ns in names_and_ns]

    def get_node_detail(self, node_name: str, namespace: str) -> dict[str, Any]:
        """Return detailed info for a specific node.

        Returns:
            Dict with publishers, subscribers, services, and clients.
        """
        full_name = f"{namespace.rstrip('/')}/{node_name}"

        publishers = self.get_publisher_names_and_types_by_node(node_name, namespace)
        subscribers = self.get_subscriber_names_and_types_by_node(node_name, namespace)
        services = self.get_service_names_and_types_by_node(node_name, namespace)
        clients = self.get_client_names_and_types_by_node(node_name, namespace)

        return {
            "name": node_name,
            "namespace": namespace,
            "full_name": full_name,
            "publishers": [{"topic": t, "types": types} for t, types in publishers],
            "subscribers": [{"topic": t, "types": types} for t, types in subscribers],
            "services": [{"name": s, "types": types} for s, types in services],
            "clients": [{"name": c, "types": types} for c, types in clients],
        }

    def get_all_topics(self) -> list[tuple[str, list[str]]]:
        """Return list of (topic_name, [type_names]) for all active topics."""
        return self.get_topic_names_and_types()

    def get_topic_info(self, topic_name: str) -> dict[str, Any]:
        """Return detailed info for a specific topic."""
        all_topics = dict(self.get_topic_names_and_types())
        types = all_topics.get(topic_name, [])

        publishers = self.get_publishers_info_by_topic(topic_name)
        subscribers = self.get_subscriptions_info_by_topic(topic_name)

        return {
            "name": topic_name,
            "types": types,
            "publisher_count": len(publishers),
            "subscriber_count": len(subscribers),
            "publishers": [
                {"node_name": info.node_name, "node_namespace": info.node_namespace}
                for info in publishers
            ],
            "subscribers": [
                {"node_name": info.node_name, "node_namespace": info.node_namespace}
                for info in subscribers
            ],
        }
