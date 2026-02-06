"""Pydantic schemas for the topics plugin."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class TopicSummary(BaseModel):
    """Brief topic info returned in list responses."""

    name: str
    types: list[str]


class TopicListResponse(BaseModel):
    """Response for GET /api/v1/topics."""

    topics: list[TopicSummary]
    count: int


class TopicEndpointInfo(BaseModel):
    """A node that publishes or subscribes to a topic."""

    node_name: str
    node_namespace: str


class TopicDetail(BaseModel):
    """Full topic info including publishers and subscribers."""

    name: str
    types: list[str]
    publisher_count: int
    subscriber_count: int
    publishers: list[TopicEndpointInfo]
    subscribers: list[TopicEndpointInfo]


class TopicStats(BaseModel):
    """Message rate statistics for a topic."""

    topic: str
    msg_count: int
    rate_hz: float
    subscriber_count: int


# --- WebSocket protocol schemas ---


class WSSubscribeAction(BaseModel):
    """Client → Server: subscribe to topic messages."""

    action: str = "subscribe"
    type: str  # e.g. "std_msgs/msg/String"


class WSUnsubscribeAction(BaseModel):
    """Client → Server: unsubscribe from topic messages."""

    action: str = "unsubscribe"


class WSDataEnvelope(BaseModel):
    """Server → Client: message data envelope."""

    type: str = "data"
    topic: str
    payload: dict[str, Any]
    timestamp: float
    seq: int


class WSStatsEnvelope(BaseModel):
    """Server → Client: stats update envelope."""

    type: str = "stats"
    topic: str
    payload: TopicStats
    timestamp: float


class WSErrorEnvelope(BaseModel):
    """Server → Client: error notification."""

    type: str = "error"
    topic: str
    payload: dict[str, str]
    timestamp: float


class WSAckEnvelope(BaseModel):
    """Server → Client: action acknowledgment."""

    type: str = "ack"
    topic: str
    payload: dict[str, str]
    timestamp: float
