# ROS 2 Web Monitor

## Project Overview

Web-based ROS 2 monitoring tool. Single-process architecture: FastAPI backend + rclpy direct integration + Vue 3 frontend.

## Tech Stack

- **Backend**: Python 3.10+, FastAPI, rclpy, uvicorn, pydantic-settings
- **Frontend**: Vue 3, TypeScript, Vite, Naive UI, Pinia
- **ROS**: ROS 2 (Humble/Jazzy), ament_python package
- **Deployment**: Docker, Docker Compose

## Architecture

```
Browser (Vue 3 SPA)
  ↕ REST + WebSocket
FastAPI Backend
  ├── Plugin Registry (nodes, topics, ...)
  └── ROS Bridge Layer (rclpy in background thread)
        ↕
      ROS 2 DDS
```

- Main thread: asyncio event loop (FastAPI/uvicorn)
- Background thread: rclpy SingleThreadedExecutor.spin()
- Communication: asyncio.Queue bridges rclpy callbacks → WebSocket handlers

## Project Structure

```
ros2_web_monitor/                    # Python package
├── main.py                          # Entry point
├── app.py                           # FastAPI app factory
├── config.py                        # Pydantic Settings
├── ros_bridge/                      # ROS 2 integration layer
│   ├── executor.py                  # Background thread executor
│   ├── node.py                      # MonitorNode (introspection)
│   ├── type_utils.py                # Message type resolution + JSON serialization
│   └── subscription_manager.py      # Dynamic subscriber lifecycle (ref-counted)
├── plugins/                         # Plugin modules (extensible)
│   ├── base.py                      # BasePlugin ABC
│   ├── registry.py                  # Auto-discovery + registration
│   ├── nodes/                       # Node monitoring plugin
│   │   ├── plugin.py, router.py, service.py, schemas.py
│   └── topics/                      # Topic monitoring plugin
│       ├── plugin.py, router.py, service.py, schemas.py
└── core/                            # Shared utilities
    ├── errors.py, middleware.py, dependencies.py

frontend/                            # Vue 3 SPA
├── src/
│   ├── views/                       # DashboardView, NodesView, TopicsView
│   ├── components/                  # layout/, nodes/, topics/, common/
│   ├── composables/                 # useWebSocket, usePolling, useRosApi
│   ├── stores/                      # Pinia: nodes, topics, connection
│   ├── api/                         # Axios client + typed API calls
│   └── types/                       # TypeScript type definitions
```

## Key Patterns

### Plugin System
Every feature is a plugin under `plugins/`. To add a new feature:
1. Create `plugins/<name>/` with `plugin.py`, `router.py`, `service.py`, `schemas.py`
2. Implement `BasePlugin` subclass
3. Add to `enabled_plugins` in config

### Dynamic Topic Subscription (ref-counted)
- First WebSocket client subscribing to a topic → creates rclpy subscription
- Additional clients → share the same subscription, each gets an asyncio.Queue
- Last client disconnects → destroys rclpy subscription
- Queue overflow → drop oldest message (preserve real-time)

### ROS Bridge Thread Safety
- Treat all cross-thread interactions as potentially unsafe unless proven otherwise.
- Prefer running ROS graph introspection (node/topic/service listing) on the ROS thread and returning results to the
  FastAPI thread via a thread-safe mechanism when feasible. If called from the FastAPI thread, document and test
  the supported ROS 2 distros (e.g., Humble/Jazzy) and keep a fallback path.
- Subscription creation/destruction must be protected (e.g., `threading.Lock`) to avoid concurrent executor access.
- `asyncio.Queue` is not thread-safe: do not call `queue.put_nowait()` directly from the rclpy spin thread. Use one of:
  - `loop.call_soon_threadsafe(queue.put_nowait, item)` (recommended)
  - A dedicated thread-bridging queue (e.g., `janus.Queue`) and have the asyncio side drain it

### Backpressure / Resource Limits
To keep the monitor responsive under high-rate topics:
- Set a bounded queue size per subscriber (or per topic shared buffer) and define an explicit drop policy
  (e.g., drop-oldest to preserve real-time).
- Consider enforcing `RWM_WS_MAX_MESSAGE_RATE` on the server side (per topic or per client) to prevent a slow
  browser from causing unbounded buffering.
- For large messages, consider sending a preview (truncated JSON) and allowing the client to request full payloads.

## API Endpoints

### Nodes Plugin
```
GET  /api/v1/nodes                           # List all active nodes
GET  /api/v1/nodes/{namespace}/{node_name}   # Node detail (pubs/subs/services)
```

### Topics Plugin
```
GET  /api/v1/topics                          # List all topics with types
GET  /api/v1/topics/{topic_name}/info        # Topic detail
GET  /api/v1/topics/{topic_name}/stats       # Message rate stats
WS   /ws/topics/{topic_name}                 # Real-time message stream
```

### WebSocket Protocol
```
Client → Server: { "action": "subscribe", "type": "std_msgs/msg/String" }
Client → Server: { "action": "unsubscribe" }
Server → Client: { "data": {...}, "timestamp": ..., "seq": ... }
Server → Client: { "stats": { "rate_hz": ..., "msg_count": ... } }
```

#### Protocol Notes (recommended)
- Version the protocol early (e.g., `protocol_version: 1`) to allow forward-compatible changes.
- Use an explicit envelope to distinguish payload types and avoid accidental field collisions, for example:
  `{ "type": "data" | "stats" | "error" | "ack", "topic": "...", "payload": ..., "timestamp": ..., "seq": ... }`.
- Validate messages with strict Pydantic schemas on the backend and typed guards on the frontend.

## Development

### Backend
```bash
# Requires ROS 2 environment sourced
source /opt/ros/humble/setup.bash
pip install -e ".[dev]"
python -m ros2_web_monitor.main
```

### Frontend
```bash
cd frontend
pnpm install
pnpm dev          # Dev server with proxy to backend :8080
pnpm build        # Production build → dist/
```

### Docker
```bash
docker compose -f docker/docker-compose.yml up -d
# Access http://localhost:8080
```

### As ROS 2 Package
```bash
colcon build --packages-select ros2_web_monitor
ros2 launch ros2_web_monitor web_monitor.launch.py port:=8080
```

## Configuration

Environment variables prefixed with `RWM_`:
- `RWM_HOST` (default: 0.0.0.0)
- `RWM_PORT` (default: 8080)
- `RWM_ROS_NODE_NAME` (default: web_monitor)
- `RWM_ROS_DOMAIN_ID` (default: from ROS_DOMAIN_ID env)
- `RWM_CORS_ORIGINS` (default: ["*"])
- `RWM_NODE_POLL_INTERVAL_SEC` (default: 2.0)
- `RWM_WS_MAX_MESSAGE_RATE` (default: 30)

### Security Notes (recommended)
- `RWM_CORS_ORIGINS=["*"]` is convenient for development but risky in production. Prefer an explicit allow-list of
  trusted origins for deployments.
- Avoid returning sensitive environment details in error payloads; log details server-side and return a generic
  message to the client.

## Testing

```bash
# Backend tests
pytest tests/backend/

# Frontend tests
cd frontend && pnpm test

# Manual verification
ros2 run demo_nodes_cpp talker &
ros2 run demo_nodes_cpp listener &
# Open http://localhost:8080 → verify nodes and topics appear
```

### Testing Notes (recommended)
- Backend unit tests:
  - Plugin registry discovery/enablement behavior
  - Subscription ref-count lifecycle (create on first subscriber, destroy on last)
  - Backpressure behavior (bounded queues, drop policy) and rate limiting
  - WebSocket protocol state machine (subscribe/unsubscribe, disconnect/reconnect, invalid messages)
- Mock external dependencies: avoid spinning a real ROS graph in unit tests; use an adapter layer and mocks for rclpy.
- Add at least one integration test suite (optional) that runs against demo nodes in CI or a dev container.

## Shutdown / Lifecycle (recommended)
Define an explicit graceful shutdown sequence to avoid hanging threads and leaked ROS entities:
1. Stop accepting new WebSocket connections; signal active handlers to unsubscribe.
2. Destroy rclpy subscriptions/publishers created by the monitor.
3. Stop the executor spin loop and join the background thread.
4. Call `rclpy.shutdown()` and close remaining asyncio tasks cleanly.

## Conventions

- Backend: Python type hints everywhere, Pydantic models for all API schemas
- Frontend: `<script setup lang="ts">`, composables for reusable logic, Pinia for state
- Naming: snake_case (Python), camelCase (TypeScript), kebab-case (Vue components)
- Each plugin is self-contained: own router, schemas, service, plugin class
- No `# type: ignore`, no `@ts-ignore`, no empty catch blocks
