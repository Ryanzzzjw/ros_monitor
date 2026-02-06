"""Message type resolution and JSON serialization utilities."""

from __future__ import annotations

import importlib
import logging
from typing import Any

from ros2_web_monitor.core.errors import MessageTypeError

logger = logging.getLogger(__name__)

# Cache resolved message classes to avoid repeated imports
_type_cache: dict[str, type] = {}


def resolve_message_type(type_name: str) -> type:
    """Resolve a ROS message type string to its Python class.

    Args:
        type_name: Fully qualified type like "std_msgs/msg/String"
                   or "std_msgs/String" (shorthand).

    Returns:
        The message class.

    Raises:
        MessageTypeError: If the type cannot be resolved.
    """
    if type_name in _type_cache:
        return _type_cache[type_name]

    parts = type_name.replace("/", ".").split(".")
    # Handle both "std_msgs/msg/String" and "std_msgs/String"
    if len(parts) == 2:
        # Shorthand: insert "msg" interface group
        parts = [parts[0], "msg", parts[1]]
    elif len(parts) != 3:
        raise MessageTypeError(type_name)

    package, interface_group, class_name = parts
    module_path = f"{package}.{interface_group}"

    try:
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
    except (ImportError, AttributeError) as exc:
        raise MessageTypeError(type_name) from exc

    _type_cache[type_name] = cls
    return cls


def message_to_dict(msg: Any) -> dict[str, Any]:
    """Convert a ROS message instance to a JSON-serializable dict.

    Recursively converts nested messages, arrays, and primitive types.
    """
    if hasattr(msg, "get_fields_and_field_types"):
        result: dict[str, Any] = {}
        for field_name in msg.get_fields_and_field_types():
            value = getattr(msg, field_name)
            result[field_name] = _convert_value(value)
        return result

    # Fallback for non-message objects
    return {"_raw": str(msg)}


def _convert_value(value: Any) -> Any:
    """Convert a single field value to a JSON-serializable form."""
    # Nested ROS message
    if hasattr(value, "get_fields_and_field_types"):
        return message_to_dict(value)

    # bytes / bytearray → hex string (avoid huge JSON arrays)
    if isinstance(value, (bytes, bytearray)):
        if len(value) <= 64:
            return list(value)
        return f"<{len(value)} bytes>"

    # numpy arrays (from ROS array fields)
    if hasattr(value, "tolist"):
        raw = value.tolist()
        if isinstance(raw, list) and len(raw) > 200:
            return raw[:200] + [f"... ({len(raw)} total)"]
        return raw

    # Regular Python list/tuple
    if isinstance(value, (list, tuple)):
        converted = [_convert_value(v) for v in value]
        if len(converted) > 200:
            return converted[:200] + [f"... ({len(converted)} total)"]
        return converted

    # Primitives (int, float, str, bool) pass through
    return value
