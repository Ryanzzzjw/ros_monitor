"""Service layer for the topics plugin."""

from __future__ import annotations

from ros2_web_monitor.core.errors import TopicNotFoundError
from ros2_web_monitor.plugins.topics.schemas import (
    TopicDetail,
    TopicEndpointInfo,
    TopicListResponse,
    TopicStats,
    TopicSummary,
)
from ros2_web_monitor.ros_bridge.node import MonitorNode
from ros2_web_monitor.ros_bridge.subscription_manager import SubscriptionManager


class TopicService:
    """Business logic for topic introspection and stats."""

    def __init__(
        self,
        monitor_node: MonitorNode,
        subscription_manager: SubscriptionManager,
    ) -> None:
        self._node = monitor_node
        self._sub_manager = subscription_manager

    def list_topics(self) -> TopicListResponse:
        """Return all active topics with their message types."""
        topics_and_types = self._node.get_all_topics()
        topics = [
            TopicSummary(name=name, types=types)
            for name, types in topics_and_types
        ]
        return TopicListResponse(topics=topics, count=len(topics))

    def get_topic_info(self, topic_name: str) -> TopicDetail:
        """Return detailed info for a specific topic.

        Raises:
            TopicNotFoundError: If the topic is not found.
        """
        info = self._node.get_topic_info(topic_name)
        if not info["types"]:
            raise TopicNotFoundError(topic_name)

        return TopicDetail(
            name=info["name"],
            types=info["types"],
            publisher_count=info["publisher_count"],
            subscriber_count=info["subscriber_count"],
            publishers=[TopicEndpointInfo(**p) for p in info["publishers"]],
            subscribers=[TopicEndpointInfo(**s) for s in info["subscribers"]],
        )

    def get_topic_stats(self, topic_name: str) -> TopicStats:
        """Return message rate stats for a topic.

        Raises:
            TopicNotFoundError: If the topic has no active subscription.
        """
        stats = self._sub_manager.get_topic_stats(topic_name)
        if stats is None:
            raise TopicNotFoundError(topic_name)
        return TopicStats(**stats)
