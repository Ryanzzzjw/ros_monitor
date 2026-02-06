# ROS 2 Web Monitor Dockerfile
FROM ros:humble-ros-base

# Install Python dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN npm install -g pnpm

# Set working directory
WORKDIR /app

# Copy Python package
COPY pyproject.toml ./
COPY ros2_web_monitor ./ros2_web_monitor/

# Install Python dependencies
RUN pip3 install --no-cache-dir -e .

# Copy and build frontend
COPY frontend ./frontend/
WORKDIR /app/frontend
RUN pnpm install && pnpm build

# Back to app root
WORKDIR /app

# Copy built frontend to static directory
RUN mkdir -p /app/static && cp -r /app/frontend/dist/* /app/static/

# Expose port
EXPOSE 8080

# Environment variables
ENV RWM_HOST=0.0.0.0
ENV RWM_PORT=8080

# Source ROS and run
CMD ["/bin/bash", "-c", "source /opt/ros/humble/setup.bash && python3 -m ros2_web_monitor.main"]
