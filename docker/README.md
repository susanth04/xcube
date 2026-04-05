# Gazebo Docker Setup

## Quick Start

Since Gazebo doesn't work natively on Windows, we use Docker to run it in Linux.

### Prerequisites

1. **Docker Desktop** with WSL2 backend (you already have this)
2. Start Docker Desktop if not running

### Build and Run

```bash
cd docker

# Build the Gazebo container (first time only, takes ~10 min)
docker-compose build gazebo-bridge

# Start Gazebo bridge
docker-compose up gazebo-bridge
```

### Connect Frontend

Your frontend at http://localhost:3000 will automatically connect to:
- Stream: http://localhost:8002/stream
- API: http://localhost:8002/health

### Without GPU

If you don't have an NVIDIA GPU or drivers, edit `docker-compose.yml` and remove the `deploy` section:

```yaml
services:
  gazebo-bridge:
    build:
      context: .
      dockerfile: Dockerfile.gazebo
    ports:
      - "8002:8002"
    environment:
      - DISPLAY=:99
    # Remove deploy section for CPU-only rendering
```

### Troubleshooting

**Container won't start:**
```bash
docker logs docker-gazebo-bridge-1
```

**Port already in use:**
Stop any local gazebo_sim_bridge.py first.

**Slow rendering:**
Gazebo uses software rendering in Docker. For better performance, use WSL2 directly with GPU passthrough.

## Alternative: Run in WSL2 Directly

For better performance, install Gazebo directly in WSL2:

```bash
# In WSL2 Ubuntu terminal
wget https://packages.osrfoundation.org/gazebo.gpg -O /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list
sudo apt update
sudo apt install gz-harmonic

# Run the bridge
cd /mnt/c/xcube
pip install fastapi uvicorn opencv-python numpy
python3 docker/gazebo_bridge_docker.py
```
