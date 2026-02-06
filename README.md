# ROS 2 Web Monitor

Web-based ROS 2 monitoring tool with real-time topic streaming.

## Features

- **Node Monitoring**: List all active ROS 2 nodes with their publishers, subscribers, services, and clients
- **Topic Monitoring**: Browse topics with message types, view publisher/subscriber info
- **Real-time Streaming**: WebSocket-based live message streaming for any topic
- **Plugin Architecture**: Extensible plugin system for adding new features

## Quick Start

### Prerequisites

- ROS 2 (Humble or Jazzy)
- Python 3.10+
- Node.js 18+ and pnpm

### Backend

```bash
# Source ROS 2
source /opt/ros/humble/setup.bash

# Install Python package
pip install -e ".[dev]"

# Run the server
python -m ros2_web_monitor.main
```

### Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

Access the UI at http://localhost:3000 (dev) or http://localhost:8080 (production).

### Docker

```bash
docker compose -f docker/docker-compose.yml up -d
```

## Configuration

Environment variables (prefix `RWM_`):

| Variable | Default | Description |
|----------|---------|-------------|
| `RWM_HOST` | 0.0.0.0 | Server bind address |
| `RWM_PORT` | 8080 | Server port |
| `RWM_ROS_NODE_NAME` | web_monitor | ROS node name |
| `RWM_ROS_DOMAIN_ID` | (from ROS_DOMAIN_ID) | ROS domain ID |
| `RWM_CORS_ORIGINS` | ["*"] | Allowed CORS origins |
| `RWM_NODE_POLL_INTERVAL_SEC` | 2.0 | Node list polling interval |
| `RWM_WS_MAX_MESSAGE_RATE` | 30 | Max WebSocket messages per second |

## API Endpoints

### Nodes
- `GET /api/v1/nodes` - List all nodes
- `GET /api/v1/nodes/{namespace}/{node_name}` - Node detail

### Topics
- `GET /api/v1/topics` - List all topics
- `GET /api/v1/topics/{topic_name}/info` - Topic detail
- `GET /api/v1/topics/{topic_name}/stats` - Message stats
- `WS /ws/topics/{topic_name}` - Real-time message stream

## Architecture

```
Browser (Vue 3 SPA)
  ↕ REST + WebSocket
FastAPI Backend
  ├── Plugin Registry
  └── ROS Bridge Layer (rclpy in background thread)
        ↕
      ROS 2 DDS
```

## License

MIT
