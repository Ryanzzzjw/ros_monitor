"""Pydantic schemas for the nodes plugin."""

from __future__ import annotations

from pydantic import BaseModel


class TopicEndpoint(BaseModel):
    """A topic with its associated message types."""

    topic: str
    types: list[str]


class ServiceEndpoint(BaseModel):
    """A service or client with its associated types."""

    name: str
    types: list[str]


class NodeSummary(BaseModel):
    """Brief node info returned in list responses."""

    name: str
    namespace: str
    full_name: str


class NodeDetail(BaseModel):
    """Full node info including publishers, subscribers, services, clients."""

    name: str
    namespace: str
    full_name: str
    publishers: list[TopicEndpoint]
    subscribers: list[TopicEndpoint]
    services: list[ServiceEndpoint]
    clients: list[ServiceEndpoint]


class NodeListResponse(BaseModel):
    """Response for GET /api/v1/nodes."""

    nodes: list[NodeSummary]
    count: int
