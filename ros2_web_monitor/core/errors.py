"""Application error types and exception hierarchy."""

from __future__ import annotations


class RWMError(Exception):
    """Base exception for all ROS Web Monitor errors."""

    def __init__(self, message: str, *, status_code: int = 500) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ROSBridgeError(RWMError):
    """Error originating from the ROS bridge layer."""

    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=503)


class PluginError(RWMError):
    """Error during plugin loading or execution."""

    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=500)


class NodeNotFoundError(RWMError):
    """Requested ROS node was not found."""

    def __init__(self, node_name: str) -> None:
        super().__init__(f"Node not found: {node_name}", status_code=404)


class TopicNotFoundError(RWMError):
    """Requested ROS topic was not found."""

    def __init__(self, topic_name: str) -> None:
        super().__init__(f"Topic not found: {topic_name}", status_code=404)


class MessageTypeError(RWMError):
    """Failed to resolve or import a ROS message type."""

    def __init__(self, type_name: str) -> None:
        super().__init__(f"Cannot resolve message type: {type_name}", status_code=400)
