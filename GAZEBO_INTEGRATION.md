# Gazebo Harmonic Integration Guide

## Overview

This project uses **Gazebo Harmonic** for physics simulation instead of NVIDIA Isaac Sim. Gazebo is an open-source robot simulation platform that's:
- Free and open-source
- Cross-platform (Windows, Linux, macOS)
- Well-documented with large community
- Lightweight compared to commercial alternatives

## Architecture

```
Frontend (React)        →  Backend API (FastAPI)  →  Gazebo Bridge  →  Gazebo Sim
:3000                      :8000                      :8002              SDF World
```

### Communication Flow

1. **User Input**: Natural language prompt via frontend
2. **Backend Processing**: Converts prompt to structured actions
3. **Gazebo Bridge**: Receives actions via HTTP, applies to simulation
4. **Gazebo Sim**: Executes physics simulation with SDF models

## Installation

### Step 1: Install Gazebo Harmonic

**Option A: Conda (Recommended for Windows)**
```bash
# Create environment
conda create -n gazebo-env python=3.10
conda activate gazebo-env

# Install Gazebo Harmonic
conda install libgz-sim8 -c conda-forge
```

**Option B: Binary Installation**
- Visit: https://gazebosim.org/docs/harmonic/install_windows
- Download and install Windows binaries
- Add to system PATH

### Step 2: Install Python Dependencies

```bash
# Activate your project environment
cd xcube
.venv\Scripts\activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Install Gazebo Python bindings
pip install gz-sim8 gz-transport13 gz-math7
```

### Step 3: Verify Installation

```bash
# Check Gazebo version
gz sim --version

# Test with sample world (GUI mode)
gz sim shapes.sdf

# Test headless mode
gz sim -s shapes.sdf
```

## Running the Bridge

### Quick Start

Use the launcher script (recommended):
```bash
# Windows
start_all.bat

# Linux/Mac
./start_all.sh
```

### Manual Start

**With Conda (Recommended):**
```bash
conda activate gazebo-env
cd xcube
python gazebo_sim_bridge.py
```

**With venv:**
```bash
# Not recommended for Gazebo - use conda instead
.venv\Scripts\activate
python gazebo_sim_bridge.py
```

The bridge will start on **http://0.0.0.0:8002**

### Verification

```bash
# Check backend health
curl http://localhost:8000/

# Check Gazebo bridge health
curl http://localhost:8002/health

# Test action execution
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Create a warehouse with one robot","session_id":"test"}'
```

## Supported Actions

### create_scene
Creates new simulation world with ground plane.

**Example:**
```json
{
  "type": "create_scene",
  "scene_name": "warehouse"
}
```

**Effect:**
- Clears existing entities
- Spawns ground plane (100x100m)
- Initializes world for new scenario

### spawn_robot
Spawns robot model at specified position.

**Example:**
```json
{
  "type": "spawn_robot",
  "robot_id": "robot_1",
  "position": [0, 0, 0.5]
}
```

**Effect:**
- Creates red cylinder (robot placeholder)
- Positioned at [x, y, z]
- Can be replaced with custom SDF robot models

### add_object
Adds cube object to scene.

**Example:**
```json
{
  "type": "add_object",
  "object_id": "box_1",
  "position": [2, 3, 0.5]
}
```

**Effect:**
- Creates blue cube (1x1x1m)
- Has physics properties (mass, inertia)
- Can interact with other objects

### move_object
Updates object position.

**Example:**
```json
{
  "type": "move_object",
  "object_id": "box_1",
  "position": [5, 5, 1]
}
```

**Effect:**
- Repositions object to new coordinates
- Maintains object properties
- Physics simulation continues from new position

### delete_object
Removes object from simulation.

**Example:**
```json
{
  "type": "delete_object",
  "object_id": "box_1"
}
```

**Effect:**
- Permanently removes entity
- Frees simulation resources
- Cannot be undone (re-spawn needed)

## Gazebo Bridge Details

### Port Configuration

- **Default Port**: 8002 (configurable in `gazebo_sim_bridge.py`)
- **Backend Expectation**: Port 8002 (set in `backend/services/gazebo_client.py`)

### Operation Modes

**GUI Mode** (Development):
- Visual feedback of simulation
- Manual inspection of scenes
- Debugging spatial relationships

**Headless Mode** (Production):
- No graphics rendering
- Lower resource usage
- Faster execution
- Automatically enabled by bridge

### SDF Format

Gazebo uses **SDFormat** (Simulation Description Format):
- XML-based scene description
- Supports physics, sensors, plugins
- Models consist of links, joints, visuals, collisions
- Version 1.9 used in this project

**Example SDF Snippet:**
```xml
<model name="my_robot">
  <pose>0 0 0.5 0 0 0</pose>
  <link name="link">
    <visual name="visual">
      <geometry>
        <cylinder>
          <radius>0.5</radius>
          <length>2.0</length>
        </cylinder>
      </geometry>
    </visual>
  </link>
</model>
```

## Troubleshooting

### Bridge Won't Start

**Problem**: Python import errors for `gz.sim8`

**Solution**:
```bash
# Verify Gazebo installation
gz sim --version

# Reinstall Python bindings
pip install --upgrade gz-sim8 gz-transport13 gz-math7

# Test import
python -c "import gz.sim8; print('Success')"
```

### Connection Refused

**Problem**: Backend can't connect to bridge

**Solution**:
1. Verify bridge is running: `curl http://localhost:8002/health`
2. Check firewall allows port 8002
3. Verify bridge logs for startup errors
4. Ensure correct port in `backend/services/gazebo_client.py`

### Actions Not Applied

**Problem**: Actions sent but nothing happens in Gazebo

**Solution**:
1. Check bridge logs for error messages
2. Verify Gazebo is actually running: `gz topic -l` (should show `/clock`)
3. Check entity names are unique
4. Ensure SDF syntax is valid
5. Restart bridge and try again

### Gazebo Not Running

**Problem**: Bridge reports "gazebo_not_running"

**Solution**:
```bash
# Start Gazebo manually in separate terminal
gz sim -s -r

# Or let bridge auto-start (default behavior)
# Check bridge logs for startup messages
```

### Performance Issues

**Problem**: Slow simulation or high CPU usage

**Solution**:
- Use headless mode (bridge uses this by default)
- Reduce world complexity
- Limit number of entities
- Check system resources
- Update graphics drivers

## Advanced Usage

### Custom Robot Models

Replace cylinder placeholder with actual robot SDF:

```python
def _generate_robot_sdf(name: str, position: List[float]) -> str:
    """Load custom robot SDF."""
    robot_sdf_path = f"models/{name}.sdf"
    
    with open(robot_sdf_path, 'r') as f:
        sdf_content = f.read()
    
    # Inject position into SDF
    # (Implementation depends on your SDF structure)
    return sdf_content
```

### Using Gazebo Fuel Models

Download pre-built models from https://app.gazebosim.org/fuel:

```bash
# Download model
gz fuel download -u https://fuel.gazebosim.org/1.0/OpenRobotics/models/Ambulance

# Models stored in: ~/.gazebo/models/
```

Reference in SDF:
```xml
<include>
  <uri>https://fuel.gazebosim.org/1.0/OpenRobotics/models/Ambulance</uri>
</include>
```

### Adding Sensors

Add camera or lidar to robots:

```xml
<sensor name="camera" type="camera">
  <camera>
    <horizontal_fov>1.047</horizontal_fov>
    <image>
      <width>640</width>
      <height>480</height>
    </image>
  </camera>
</sensor>
```

### Physics Tuning

Adjust physics parameters in SDF:

```xml
<physics name="1ms" type="ignored">
  <max_step_size>0.001</max_step_size>
  <real_time_factor>1.0</real_time_factor>
</physics>
```

## Distributed Setup

### Gazebo on Remote Machine

**On Gazebo Machine:**
```bash
# Run bridge with external binding
python gazebo_sim_bridge.py --host 0.0.0.0
```

**On Backend Machine:**

Edit `backend/services/gazebo_client.py`:
```python
gazebo_client = create_gazebo_client(
    host="192.168.1.100",  # Gazebo machine IP
    port=8002
)
```

## Monitoring & Debugging

### View Gazebo Topics

```bash
# List all topics
gz topic -l

# Echo topic data
gz topic -e -t /world/default/pose/info

# Get model info
gz model -m robot_1 -i
```

### Bridge Logging

Bridge logs all actions to console:
```
INFO:__main__:Applied create_scene: {'type': 'create_scene', 'scene_name': 'warehouse'}
INFO:__main__:Spawned robot: robot_1 at [0, 0, 0.5]
INFO:__main__:Added object: box_1 at [2, 3, 0.5]
```

### Check Service Availability

```bash
# List available services
gz service -l

# Call service manually
gz service -s /world/default/create --reqtype gz.msgs.StringMsg --reptype gz.msgs.Boolean --timeout 1000 --req 'data: "<sdf>...</sdf>"'
```

## Migration from Isaac Sim

### Key Differences

| Aspect | Isaac Sim | Gazebo Harmonic |
|--------|-----------|-----------------|
| Format | USD | SDF |
| License | Proprietary | Open Source |
| Platform | NVIDIA GPU required | Any GPU/CPU |
| Python API | `omni.isaac.kit` | `gz.sim8` |
| Port | 8001 | 8002 |

### File Changes Made

**Replaced:**
- `isaac_sim_bridge.py` → `gazebo_sim_bridge.py`
- `backend/services/isaac_client.py` → `backend/services/gazebo_client.py`
- `ISAAC_INTEGRATION.md` → `GAZEBO_INTEGRATION.md`

**Updated:**
- `backend/api_server.py` (uses `gazebo_client` instead of `isaac_client`)
- `backend/requirements.txt` (added Gazebo dependencies)
- `README.md` (updated all references)

### Data Migration

No data migration needed - state is managed by backend's `scene_manager`, which is simulator-agnostic.

## Resources

- **Gazebo Documentation**: https://gazebosim.org/docs/harmonic
- **Python API Reference**: https://gazebosim.org/api/sim/8/
- **SDF Specification**: http://sdformat.org/spec
- **Model Library**: https://app.gazebosim.org/fuel
- **Community Forum**: https://community.gazebosim.org/
- **GitHub**: https://github.com/gazebosim/gz-sim

## Related Files

- `gazebo_sim_bridge.py` - Bridge implementation
- `backend/services/gazebo_client.py` - HTTP client
- `GAZEBO_INSTALLATION.md` - Installation guide
- `README.md` - Main documentation

---

**Version**: 1.0.0  
**Gazebo Harmonic Version**: 8.x  
**Last Updated**: April 2026
