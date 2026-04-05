#!/bin/bash
# Launch script for X_Cube Gazebo Simulation System (Linux/Mac)
# Starts all required services

echo "============================================================"
echo "X_Cube Gazebo Simulation System - Launcher"
echo "============================================================"
echo ""

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "ERROR: Conda not found! Please install Miniconda or Anaconda."
    echo "Visit: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Starting services..."
echo ""

# Activate conda environment and start Gazebo Bridge
echo "[1/2] Starting Gazebo Bridge on port 8002..."
gnome-terminal --title="Gazebo Bridge" -- bash -c "conda activate gazebo-env && python gazebo_sim_bridge.py; exec bash" 2>/dev/null || \
xterm -title "Gazebo Bridge" -e "conda activate gazebo-env && python gazebo_sim_bridge.py; bash" 2>/dev/null || \
bash -c "conda activate gazebo-env && python gazebo_sim_bridge.py" &

sleep 3

# Activate conda environment and start Backend API
echo "[2/2] Starting Backend API on port 8000..."
gnome-terminal --title="Backend API" -- bash -c "conda activate gazebo-env && python -m uvicorn backend.api_server:app --host 0.0.0.0 --port 8000; exec bash" 2>/dev/null || \
xterm -title "Backend API" -e "conda activate gazebo-env && python -m uvicorn backend.api_server:app --host 0.0.0.0 --port 8000; bash" 2>/dev/null || \
bash -c "conda activate gazebo-env && python -m uvicorn backend.api_server:app --host 0.0.0.0 --port 8000" &

sleep 3

echo ""
echo "============================================================"
echo "All services started!"
echo "============================================================"
echo ""
echo "Services:"
echo "  - Gazebo Bridge:  http://localhost:8002/health"
echo "  - Backend API:    http://localhost:8000/"
echo ""
echo "To start the frontend (optional):"
echo "  cd simulation-ui"
echo "  npm run dev"
echo ""
echo "Press Ctrl+C to stop all services"

# Keep script running
wait
