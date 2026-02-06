"""Entry point for the ROS 2 Web Monitor."""

from __future__ import annotations

import logging
import sys


def main() -> None:
    """Start the ROS 2 Web Monitor server."""
    # Configure logging before anything else
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Import after logging is configured
    import uvicorn

    from ros2_web_monitor.app import create_app
    from ros2_web_monitor.config import Settings

    settings = Settings()
    app = create_app(settings)

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
