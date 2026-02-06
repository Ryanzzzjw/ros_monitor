"""Service layer for the nodes plugin."""

from __future__ import annotations

from ros2_web_monitor.core.errors import NodeNotFoundError
from ros2_web_monitor.plugins.nodes.schemas import NodeDetail, NodeListResponse, NodeSummary
from ros2_web_monitor.ros_bridge.node import MonitorNode


class NodeService:
    """Business logic for node introspection."""

    def __init__(self, monitor_node: MonitorNode) -> None:
        self._node = monitor_node

    def list_nodes(self) -> NodeListResponse:
        """Return all discovered ROS nodes."""
        names_and_ns = self._node.get_node_names_with_namespaces()
        nodes = [
            NodeSummary(
                name=name,
                namespace=ns,
                full_name=f"{ns.rstrip('/')}/{name}",
            )
            for name, ns in names_and_ns
        ]
        return NodeListResponse(nodes=nodes, count=len(nodes))

    def get_node_detail(self, namespace: str, node_name: str) -> NodeDetail:
        """Return detailed info for a specific node.

        Raises:
            NodeNotFoundError: If the node is not found in the graph.
        """
        # Verify node exists
        names_and_ns = self._node.get_node_names_with_namespaces()
        found = any(n == node_name and ns == namespace for n, ns in names_and_ns)
        if not found:
            raise NodeNotFoundError(f"{namespace}/{node_name}")

        detail = self._node.get_node_detail(node_name, namespace)
        return NodeDetail(**detail)
