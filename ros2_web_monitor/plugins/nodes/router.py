"""FastAPI router for the nodes plugin."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ros2_web_monitor.core.dependencies import get_monitor_node
from ros2_web_monitor.plugins.nodes.schemas import NodeDetail, NodeListResponse
from ros2_web_monitor.plugins.nodes.service import NodeService
from ros2_web_monitor.ros_bridge.node import MonitorNode

router = APIRouter(prefix="/api/v1/nodes", tags=["nodes"])


def _get_service(node: MonitorNode = Depends(get_monitor_node)) -> NodeService:
    return NodeService(node)


@router.get("", response_model=NodeListResponse)
async def list_nodes(service: NodeService = Depends(_get_service)) -> NodeListResponse:
    """List all active ROS nodes."""
    return service.list_nodes()


@router.get("/{namespace:path}/{node_name}", response_model=NodeDetail)
async def get_node_detail(
    namespace: str,
    node_name: str,
    service: NodeService = Depends(_get_service),
) -> NodeDetail:
    """Get detailed info for a specific node (publishers, subscribers, services, clients).

    The namespace path may contain slashes, e.g. /my/namespace/node_name.
    """
    # Ensure namespace starts with /
    if not namespace.startswith("/"):
        namespace = f"/{namespace}"
    return service.get_node_detail(namespace, node_name)
