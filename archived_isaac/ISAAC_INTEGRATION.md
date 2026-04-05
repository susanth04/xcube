# Isaac Sim Integration Guide

## Setup Instructions

### Step 1: Verify Isaac Sim Installation

```bash
# Check Isaac Sim is installed
%ISAAC_SIM_ROOT%/isaac-sim.sh --version

# Or on Linux
$ISAAC_SIM_ROOT/isaac-sim.sh --version
```

### Step 2: Create Isaac Python Environment

```bash
# Run Isaac python setup
%ISAAC_SIM_ROOT%/python.bat -m venv isaac_env

# Activate
isaac_env\Scripts\activate.bat  # Windows
source isaac_env/bin/activate   # Linux
```

### Step 3: Install Dependencies in Isaac Environment

```bash
# With isaac_env activated:
pip install fastapi uvicorn pydantic requests
```

### Step 4: Copy Bridge Script

```bash
# Copy isaac_sim_bridge.py to Isaac Sim directory
cp isaac_sim_bridge.py %ISAAC_SIM_ROOT%/
```

### Step 5: Start Isaac Sim and Bridge

**Option A: With GUI**
```bash
# Terminal 1: Start Isaac Sim
%ISAAC_SIM_ROOT%/isaac-sim.sh

# Terminal 2: Run bridge (with isaac_env activated)
cd %ISAAC_SIM_ROOT%
python isaac_sim_bridge.py
```

**Option B: Headless**
```bash
# Direct command
%ISAAC_SIM_ROOT%/python.bat isaac_sim_bridge.py
```

### Step 6: Verify Connection

```bash
# Check bridge health
curl http://localhost:8001/health

# Should return:
# {"status":"ok","isaac_available":true}
```

---

## Network Setup (Distributed)

If Isaac Sim is on a different machine:

### On Isaac Machine:
1. Note the machine IP: `ipconfig` (Windows) or `ifconfig` (Linux)
2. Start bridge with IP binding:
   ```bash
   python isaac_sim_bridge.py --host 0.0.0.0
   ```

### On Backend Machine:
Edit `backend/services/isaac_client.py`:
```python
isaac_client = create_isaac_client(
    host="<isaac-machine-ip>",  # e.g. "192.168.1.100"
    port=8001
)
```

---

## Troubleshooting

### Bridge Won't Start
```bash
# Check Isaac environment
python -c "from pxr import Usd; print('OK')"

# If error: reinstall USD/OmniClient
pip install pxr
```

### No USD Stage
- Isaac Sim GUI may not be ready
- Wait 5 seconds after starting
- Check Isaac Sim console for errors

### Connection Refused
- Verify bridge is running: `curl http://localhost:8001/health`
- Check firewall for port 8001
- Verify network connectivity

### Actions Not Applied
- Check Isaac Sim console for error messages
- Verify stage path exists: `/World/`
- Restart bridge and try again

---

## Action Processing

### What Happens When Action is Received

```
POST /apply_actions
    ↓
Parse action payload
    ↓
Get USD stage
    ↓
Apply action (create/spawn/move/delete)
    ↓
Return response
    ↓
API Response
```

### Example Session

```
Step 1: create_scene
→ Stage cleared, /World/default_ground created

Step 2: spawn_robot
→ /World/robot_1 (cylinder) created at [0,0,0.5]

Step 3: add_object
→ /World/object_1 (cube) created at [0,0,0]

Step 4: move_object
→ /World/object_1 transform updated to [5,1,2]

Step 5: delete_object
→ /World/object_1 removed
```

---

## Performance Tuning

### For Better Performance

1. **Increase Timeout** (for complex scenes):
   ```python
   isaac_client = create_isaac_client(
       host="localhost",
       port=8001,
       timeout=30  # Increase from default 10
   )
   ```

2. **Batch Actions**:
   - Send multiple actions in one request
   - Reduces HTTP overhead

3. **Use Headless Mode**:
   - No GUI rendering = faster processing
   - Recommended for production

---

## Monitoring

### Check Isaac Bridge Logs

Bridge logs all actions to console:
```
INFO:__main__:Applied create_scene: {'type': 'create_scene', 'scene_name': 'warehouse'}
INFO:__main__:Applied spawn_robot: {'type': 'spawn_robot', ...}
```

### Monitor Stage

```python
# Inside Isaac, inspect stage:
from pxr import Usd
stage = Usd.Stage.Open("/World/scene.usd")
print(stage.GetPrimAtPath("/World"))
```

---

## Advanced Usage

### Custom USD Assets

Instead of primitives (cube, cylinder), load real USD models:

```python
def _spawn_robot_action(stage: Any, action: Dict[str, Any]) -> None:
    """Load real robot USD instead of cylinder."""
    robot_id = action.get("robot_id", "robot")
    position = action.get("position", [0, 0, 0])
    
    # Load USD instead of creating primitive
    usd_path = f"/path/to/models/{robot_id}.usd"
    prim = stage.DefinePrim(f"/World/{robot_id}", "Xform")
    prim.GetReferences().AddReference(usd_path)
    
    # Apply transform
    prim.AddTransformOp().Set(
        Gf.Matrix4d().SetTranslate(Gf.Vec3d(*position))
    )
```

### Physics Simulation

Add physics properties:
```python
def _add_physics(stage: Any, prim_path: str) -> None:
    """Add physics to prim."""
    prim = stage.GetPrimAtPath(prim_path)
    
    # Add rigid body
    from pxr import UsdPhysics
    rigid = UsdPhysics.RigidBodyAPI.Apply(prim)
    
    # Add collider
    UsdPhysics.CollisionAPI.Apply(prim)
```

---

## Related Files

- `isaac_sim_bridge.py` - Bridge implementation
- `backend/services/isaac_client.py` - Client code
- `SYSTEM_CONTEXT.md` - Full architecture guide

---

**Version**: 1.0.0  
**Last Updated**: April 2026
