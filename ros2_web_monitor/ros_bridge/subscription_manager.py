"""Dynamic subscriber lifecycle management with ref-counting.

First WebSocket client subscribing to a topic → creates rclpy subscription.
Additional clients → share the same subscription, each gets an asyncio.Queue.
Last client disconnects → destroys rclpy subscription.
Queue overflow → drop oldest message (preserve real-time).
"""

from __future__ import annotations

import asyncio
import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Any

from ros2_web_monitor.ros_bridge.type_utils import message_to_dict, resolve_message_type

logger = logging.getLogger(__name__)


@dataclass
class _TopicSubscription:
    """Internal state for a single shared topic subscription."""

    topic_name: str
    message_type: str
    ros_subscription: Any  # rclpy Subscription object
    queues: dict[str, asyncio.Queue[dict[str, Any]]] = field(default_factory=dict)
    msg_count: int = 0
    last_msg_time: float = 0.0
    created_at: float = field(default_factory=time.monotonic)


class SubscriptionManager:
    """Manages ref-counted ROS topic subscriptions shared across WebSocket clients.

    Thread safety:
    - Subscription creation/destruction is protected by a threading.Lock
      to avoid concurrent executor access.
    - Message delivery uses loop.call_soon_threadsafe to bridge from the
      rclpy spin thread to the asyncio event loop.
    """

    def __init__(
        self,
        node: Any,  # MonitorNode
        loop: asyncio.AbstractEventLoop,
        *,
        queue_size: int = 50,
    ) -> None:
        self._node = node
        self._loop = loop
        self._queue_size = queue_size
        self._lock = threading.Lock()
        self._subscriptions: dict[str, _TopicSubscription] = {}
        self._seq_counters: dict[str, int] = {}

    def subscribe(
        self,
        client_id: str,
        topic_name: str,
        message_type: str,
    ) -> asyncio.Queue[dict[str, Any]]:
        """Add a client subscription to a topic. Returns the client's message queue.

        If this is the first client for the topic, creates the rclpy subscription.
        """
        with self._lock:
            if topic_name in self._subscriptions:
                sub = self._subscriptions[topic_name]
                queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=self._queue_size)
                sub.queues[client_id] = queue
                logger.info(
                    "Client %s joined topic %s (ref_count=%d)",
                    client_id, topic_name, len(sub.queues),
                )
                return queue

            # First subscriber — create rclpy subscription
            msg_cls = resolve_message_type(message_type)
            queue = asyncio.Queue(maxsize=self._queue_size)
            self._seq_counters[topic_name] = 0

            def _callback(msg: Any) -> None:
                self._on_message(topic_name, msg)

            ros_sub = self._node.create_subscription(
                msg_cls,
                topic_name,
                _callback,
                10,  # QoS depth
            )

            sub = _TopicSubscription(
                topic_name=topic_name,
                message_type=message_type,
                ros_subscription=ros_sub,
                queues={client_id: queue},
            )
            self._subscriptions[topic_name] = sub
            logger.info("Created rclpy subscription for topic %s", topic_name)
            return queue

    def unsubscribe(self, client_id: str, topic_name: str) -> None:
        """Remove a client subscription. Destroys rclpy subscription if last client."""
        with self._lock:
            sub = self._subscriptions.get(topic_name)
            if sub is None:
                return

            sub.queues.pop(client_id, None)
            logger.info(
                "Client %s left topic %s (ref_count=%d)",
                client_id, topic_name, len(sub.queues),
            )

            if not sub.queues:
                # Last client — destroy rclpy subscription
                self._node.destroy_subscription(sub.ros_subscription)
                del self._subscriptions[topic_name]
                self._seq_counters.pop(topic_name, None)
                logger.info("Destroyed rclpy subscription for topic %s", topic_name)

    def unsubscribe_all(self, client_id: str) -> None:
        """Remove a client from all topic subscriptions (on disconnect)."""
        with self._lock:
            topics_to_remove: list[str] = []
            for topic_name, sub in self._subscriptions.items():
                if client_id in sub.queues:
                    del sub.queues[client_id]
                    if not sub.queues:
                        topics_to_remove.append(topic_name)

            for topic_name in topics_to_remove:
                sub = self._subscriptions.pop(topic_name)
                self._node.destroy_subscription(sub.ros_subscription)
                self._seq_counters.pop(topic_name, None)
                logger.info(
                    "Destroyed rclpy subscription for topic %s (client %s disconnected)",
                    topic_name, client_id,
                )

    def get_topic_stats(self, topic_name: str) -> dict[str, Any] | None:
        """Return message rate stats for a subscribed topic."""
        sub = self._subscriptions.get(topic_name)
        if sub is None:
            return None

        elapsed = time.monotonic() - sub.created_at
        rate_hz = sub.msg_count / elapsed if elapsed > 0 else 0.0

        return {
            "topic": topic_name,
            "msg_count": sub.msg_count,
            "rate_hz": round(rate_hz, 2),
            "subscriber_count": len(sub.queues),
        }

    def _on_message(self, topic_name: str, msg: Any) -> None:
        """Callback invoked from the rclpy spin thread.

        Uses loop.call_soon_threadsafe to safely deliver to asyncio queues.
        """
        sub = self._subscriptions.get(topic_name)
        if sub is None:
            return

        sub.msg_count += 1
        sub.last_msg_time = time.monotonic()

        self._seq_counters[topic_name] = self._seq_counters.get(topic_name, 0) + 1
        seq = self._seq_counters[topic_name]

        data = message_to_dict(msg)
        envelope = {
            "type": "data",
            "topic": topic_name,
            "payload": data,
            "timestamp": time.time(),
            "seq": seq,
        }

        # Bridge from rclpy thread → asyncio event loop
        self._loop.call_soon_threadsafe(self._distribute, topic_name, envelope)

    def _distribute(self, topic_name: str, envelope: dict[str, Any]) -> None:
        """Distribute a message to all client queues (runs on asyncio thread)."""
        sub = self._subscriptions.get(topic_name)
        if sub is None:
            return

        for client_id, queue in list(sub.queues.items()):
            if queue.full():
                # Drop oldest to preserve real-time
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass
            try:
                queue.put_nowait(envelope)
            except asyncio.QueueFull:
                logger.debug("Queue full for client %s on topic %s", client_id, topic_name)

    def shutdown(self) -> None:
        """Destroy all rclpy subscriptions."""
        with self._lock:
            for topic_name, sub in list(self._subscriptions.items()):
                self._node.destroy_subscription(sub.ros_subscription)
                logger.info("Shutdown: destroyed subscription for %s", topic_name)
            self._subscriptions.clear()
            self._seq_counters.clear()
