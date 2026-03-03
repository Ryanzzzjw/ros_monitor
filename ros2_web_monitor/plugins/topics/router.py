"""FastAPI router for the topics plugin (REST + WebSocket)."""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import suppress
from typing import Any

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from ros2_web_monitor.core.dependencies import get_monitor_node, get_subscription_manager
from ros2_web_monitor.plugins.topics.schemas import (
    TopicDetail,
    TopicListResponse,
    TopicStats,
)
from ros2_web_monitor.plugins.topics.service import TopicService
from ros2_web_monitor.ros_bridge.node import MonitorNode
from ros2_web_monitor.ros_bridge.subscription_manager import SubscriptionManager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["topics"])


def _get_service(
    node: MonitorNode = Depends(get_monitor_node),
    sub_manager: SubscriptionManager = Depends(get_subscription_manager),
) -> TopicService:
    return TopicService(node, sub_manager)


# --- REST endpoints ---


@router.get("/api/v1/topics", response_model=TopicListResponse)
async def list_topics(service: TopicService = Depends(_get_service)) -> TopicListResponse:
    """List all topics with their message types."""
    return service.list_topics()


@router.get("/api/v1/topics/{topic_name:path}/info", response_model=TopicDetail)
async def get_topic_info(
    topic_name: str,
    service: TopicService = Depends(_get_service),
) -> TopicDetail:
    """Get detailed info for a specific topic."""
    if not topic_name.startswith("/"):
        topic_name = f"/{topic_name}"
    return service.get_topic_info(topic_name)


@router.get("/api/v1/topics/{topic_name:path}/stats", response_model=TopicStats)
async def get_topic_stats(
    topic_name: str,
    service: TopicService = Depends(_get_service),
) -> TopicStats:
    """Get message rate statistics for a topic."""
    if not topic_name.startswith("/"):
        topic_name = f"/{topic_name}"
    return service.get_topic_stats(topic_name)


# --- WebSocket endpoint ---


@router.websocket("/ws/topics/{topic_name:path}")
async def topic_websocket(
    websocket: WebSocket,
    topic_name: str,
) -> None:
    """Real-time message stream for a topic via WebSocket.

    Protocol:
        Client → Server: { "action": "subscribe", "type": "std_msgs/msg/String" }
        Client → Server: { "action": "unsubscribe" }
        Server → Client: { "type": "data"|"stats"|"error"|"ack", "topic": ..., "payload": ..., ... }
    """
    await websocket.accept()

    if not topic_name.startswith("/"):
        topic_name = f"/{topic_name}"

    client_id = str(uuid.uuid4())[:8]
    sub_manager: SubscriptionManager = get_subscription_manager()
    subscribed = False
    send_task: asyncio.Task[None] | None = None

    logger.info("WebSocket client %s connected for topic %s", client_id, topic_name)

    try:
        async for raw in _client_messages(websocket):
            action = raw.get("action")

            if action == "subscribe" and not subscribed:
                msg_type = raw.get("type", "")
                if not msg_type:
                    await _send_error(websocket, topic_name, "Missing 'type' field")
                    continue

                try:
                    queue = sub_manager.subscribe(client_id, topic_name, msg_type)
                    subscribed = True
                    await _send_ack(websocket, topic_name, "subscribed")
                    # Start sending messages
                    send_task = asyncio.create_task(
                        _send_loop(websocket, queue, client_id, topic_name, sub_manager)
                    )
                except Exception as exc:
                    await _send_error(websocket, topic_name, str(exc))

            elif action == "unsubscribe" and subscribed:
                await _cancel_task(send_task)
                send_task = None
                sub_manager.unsubscribe(client_id, topic_name)
                subscribed = False
                await _send_ack(websocket, topic_name, "unsubscribed")

            else:
                await _send_error(
                    websocket, topic_name,
                    f"Invalid action '{action}' (subscribed={subscribed})",
                )

    except WebSocketDisconnect:
        logger.info("WebSocket client %s disconnected", client_id)
    except Exception:
        logger.exception("WebSocket error for client %s", client_id)
    finally:
        await _cancel_task(send_task)
        # Clean up all subscriptions for this client
        sub_manager.unsubscribe_all(client_id)
        logger.info("WebSocket client %s cleaned up", client_id)


async def _client_messages(
    websocket: WebSocket,
) -> AsyncIterator[dict[str, Any]]:
    """Async generator that yields parsed JSON messages from the client."""
    while True:
        raw_text = await websocket.receive_text()
        try:
            data = json.loads(raw_text)
            if isinstance(data, dict):
                yield data
            else:
                logger.warning("Ignored non-object WebSocket message from client")
        except json.JSONDecodeError:
            logger.warning("Invalid JSON from client: %s", raw_text[:100])


async def _send_loop(
    websocket: WebSocket,
    queue: asyncio.Queue[dict[str, Any]],
    client_id: str,
    topic_name: str,
    sub_manager: SubscriptionManager,
) -> None:
    """Send messages from the queue to the WebSocket client."""
    stats_interval = 5.0  # Send stats every 5 seconds
    last_stats_time = time.monotonic()

    try:
        while True:
            try:
                envelope = await asyncio.wait_for(queue.get(), timeout=1.0)
                await websocket.send_json(envelope)
            except asyncio.TimeoutError:
                pass

            # Periodically send stats
            now = time.monotonic()
            if now - last_stats_time >= stats_interval:
                last_stats_time = now
                stats = sub_manager.get_topic_stats(topic_name)
                if stats is not None:
                    stats_envelope = {
                        "type": "stats",
                        "topic": topic_name,
                        "payload": stats,
                        "timestamp": time.time(),
                    }
                    await websocket.send_json(stats_envelope)

    except asyncio.CancelledError:
        return
    except Exception:
        logger.exception("Send loop error for client %s", client_id)


async def _cancel_task(task: asyncio.Task[None] | None) -> None:
    """Cancel an async task and wait for it to finish."""
    if task is None:
        return

    task.cancel()
    with suppress(asyncio.CancelledError):
        await task


async def _send_error(websocket: WebSocket, topic_name: str, message: str) -> None:
    """Send an error envelope to the client."""
    await websocket.send_json({
        "type": "error",
        "topic": topic_name,
        "payload": {"message": message},
        "timestamp": time.time(),
    })


async def _send_ack(websocket: WebSocket, topic_name: str, action: str) -> None:
    """Send an acknowledgment envelope to the client."""
    await websocket.send_json({
        "type": "ack",
        "topic": topic_name,
        "payload": {"action": action},
        "timestamp": time.time(),
    })
