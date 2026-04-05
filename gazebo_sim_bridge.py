"""
Gazebo Harmonic HTTP server.
Runs as standalone service and communicates with Gazebo simulation.
Receives actions and applies them to Gazebo world.

Run with:
    python gazebo_sim_bridge.py
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import subprocess
import os
import time

# Gazebo imports
try:
    import gz.sim8 as gz_sim
    import gz.math7 as gz_math
    import gz.transport13 as gz_transport
    GAZEBO_AVAILABLE = True
except ImportError:
    GAZEBO_AVAILABLE = False
    print("Warning: Gazebo imports not available - mock mode active")


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Gazebo Sim Bridge",
    description="Receives and applies simulation actions to Gazebo Harmonic",
    version="1.0.0"
)


class ActionPayload(BaseModel):
    """Action payload from backend."""
    actions: List[Dict[str, Any]]


# Gazebo state
gazebo_process = None
node = None
entity_manager = {}  # Track spawned entities


@app.on_event("startup")
async def startup_event():
    """Initialize Gazebo on startup."""
    global gazebo_process, node
    
    if not GAZEBO_AVAILABLE:
        logger.warning("Gazebo not available - running in mock mode")
        return
    
    try:
        # Initialize Gazebo transport node
        node = gz_transport.Node()
        logger.info("Gazebo transport node initialized")
        
        # Check if Gazebo is already running
        if not _is_gazebo_running():
            logger.info("Starting Gazebo in headless mode...")
            # Start Gazebo server in headless mode with empty world
            gazebo_process = subprocess.Popen(
                ["gz", "sim", "-s", "-r", "--headless-rendering", "-v", "4"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            # Give Gazebo time to start
            time.sleep(3)
            logger.info("Gazebo server started")
        else:
            logger.info("Gazebo already running")
            
    except Exception as e:
        logger.error(f"Failed to initialize Gazebo: {str(e)}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global gazebo_process
    
    if gazebo_process:
        logger.info("Stopping Gazebo server...")
        gazebo_process.terminate()
        gazebo_process.wait(timeout=5)


def _is_gazebo_running() -> bool:
    """Check if Gazebo server is running."""
    try:
        result = subprocess.run(
            ["gz", "topic", "-l"],
            capture_output=True,
            text=True,
            timeout=2
        )
        return "/clock" in result.stdout
    except:
        return False


@app.get("/health")
async def health():
    """Health check."""
    if not GAZEBO_AVAILABLE:
        return {"status": "mock_mode", "gazebo_available": False}
    
    is_running = _is_gazebo_running()
    
    return {
        "status": "ok" if is_running else "gazebo_not_running",
        "gazebo_available": True,
        "gazebo_running": is_running
    }


@app.post("/apply_actions")
async def apply_actions(payload: ActionPayload):
    """
    Apply actions to Gazebo simulation.
    
    Supported actions:
    - create_scene: Create new world
    - spawn_robot: Spawn robot model
    - add_object: Create object (cube)
    - move_object: Update entity pose
    - delete_object: Remove entity
    
    Args:
        payload: ActionPayload with list of actions
        
    Returns:
        Response with status and results
    """
    if not GAZEBO_AVAILABLE:
        logger.warning("Gazebo not available - actions not applied")
        return {"status": "mock_mode", "actions_applied": 0}
    
    if not _is_gazebo_running():
        raise HTTPException(status_code=503, detail="Gazebo server not running")
    
    results = []
    
    try:
        for action in payload.actions:
            action_type = action.get("type")
            result = {"action": action_type, "success": False}
            
            try:
                if action_type == "create_scene":
                    _create_scene_action(action)
                    result["success"] = True
                
                elif action_type == "spawn_robot":
                    _spawn_robot_action(action)
                    result["success"] = True
                
                elif action_type == "add_object":
                    _add_object_action(action)
                    result["success"] = True
                
                elif action_type == "move_object":
                    _move_object_action(action)
                    result["success"] = True
                
                elif action_type == "delete_object":
                    _delete_object_action(action)
                    result["success"] = True
                
                else:
                    result["error"] = f"Unknown action type: {action_type}"
                
                if result["success"]:
                    logger.info(f"Applied {action_type}: {action}")
            
            except Exception as e:
                result["error"] = str(e)
                logger.error(f"Failed to apply {action_type}: {str(e)}")
            
            results.append(result)
        
        return {
            "status": "ok",
            "actions_applied": len([r for r in results if r["success"]]),
            "results": results
        }
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def _create_scene_action(action: Dict[str, Any]) -> None:
    """Create new scene by clearing existing entities."""
    global entity_manager
    
    scene_name = action.get("scene_name", "default")
    
    # Clear all tracked entities
    for entity_id in list(entity_manager.keys()):
        try:
            _delete_entity(entity_id)
        except Exception as e:
            logger.warning(f"Failed to delete entity {entity_id}: {e}")
    
    entity_manager.clear()
    
    # Spawn ground plane
    ground_sdf = _generate_ground_plane_sdf(scene_name)
    _spawn_entity(f"{scene_name}_ground", ground_sdf)
    
    logger.info(f"Created scene: {scene_name}")


def _spawn_robot_action(action: Dict[str, Any]) -> None:
    """Spawn robot in the world."""
    robot_id = action.get("robot_id", "robot")
    position = action.get("position", [0, 0, 0.5])
    
    # Generate robot SDF (cylinder as placeholder)
    robot_sdf = _generate_robot_sdf(robot_id, position)
    _spawn_entity(robot_id, robot_sdf)
    
    entity_manager[robot_id] = {"type": "robot", "position": position}
    logger.info(f"Spawned robot: {robot_id} at {position}")


def _add_object_action(action: Dict[str, Any]) -> None:
    """Add object (cube) to the world."""
    object_id = action.get("object_id", "object")
    position = action.get("position", [0, 0, 0.5])
    
    # Generate cube SDF
    cube_sdf = _generate_cube_sdf(object_id, position)
    _spawn_entity(object_id, cube_sdf)
    
    entity_manager[object_id] = {"type": "object", "position": position}
    logger.info(f"Added object: {object_id} at {position}")


def _move_object_action(action: Dict[str, Any]) -> None:
    """Move object to new position."""
    object_id = action.get("object_id", "object")
    position = action.get("position", [0, 0, 0])
    
    # Use Gazebo transport to set entity pose
    _set_entity_pose(object_id, position)
    
    if object_id in entity_manager:
        entity_manager[object_id]["position"] = position
    
    logger.info(f"Moved object: {object_id} to {position}")


def _delete_object_action(action: Dict[str, Any]) -> None:
    """Delete object from world."""
    object_id = action.get("object_id", "object")
    
    _delete_entity(object_id)
    
    if object_id in entity_manager:
        del entity_manager[object_id]
    
    logger.info(f"Deleted object: {object_id}")


def _spawn_entity(name: str, sdf_content: str) -> None:
    """Spawn entity using Gazebo service."""
    global node
    
    # Create request message
    req = gz_transport.StringMsg()
    req.data = sdf_content
    
    # Call spawn service
    service = "/world/default/create"
    
    timeout = 1000  # milliseconds
    executed, response = node.request(service, req, timeout=timeout)
    
    if not executed:
        raise Exception(f"Failed to spawn entity {name}: Service call timeout")


def _delete_entity(name: str) -> None:
    """Delete entity using Gazebo service."""
    global node
    
    # Create request
    req = gz_transport.StringMsg()
    req.data = name
    
    # Call remove service
    service = "/world/default/remove"
    
    timeout = 1000
    executed, response = node.request(service, req, timeout=timeout)
    
    if not executed:
        raise Exception(f"Failed to delete entity {name}: Service call timeout")


def _set_entity_pose(name: str, position: List[float]) -> None:
    """Set entity pose using Gazebo transport."""
    global node
    
    # Publish to pose topic
    topic = f"/model/{name}/pose"
    
    # Create pose publisher
    pub = node.advertise(topic, "gz.msgs.Pose")
    
    # Create pose message (simplified - would need proper gz.msgs.Pose)
    # For now, we'll delete and respawn at new location
    # This is a workaround - proper implementation would use pose service
    if name in entity_manager:
        entity_info = entity_manager[name]
        _delete_entity(name)
        
        if entity_info["type"] == "robot":
            robot_sdf = _generate_robot_sdf(name, position)
            _spawn_entity(name, robot_sdf)
        else:
            cube_sdf = _generate_cube_sdf(name, position)
            _spawn_entity(name, cube_sdf)


def _generate_ground_plane_sdf(name: str) -> str:
    """Generate SDF for ground plane."""
    return f"""<?xml version="1.0" ?>
<sdf version="1.9">
  <model name="{name}">
    <static>true</static>
    <link name="link">
      <collision name="collision">
        <geometry>
          <plane>
            <normal>0 0 1</normal>
            <size>100 100</size>
          </plane>
        </geometry>
      </collision>
      <visual name="visual">
        <geometry>
          <plane>
            <normal>0 0 1</normal>
            <size>100 100</size>
          </plane>
        </geometry>
        <material>
          <ambient>0.5 0.5 0.5 1</ambient>
          <diffuse>0.5 0.5 0.5 1</diffuse>
        </material>
      </visual>
    </link>
  </model>
</sdf>"""


def _generate_robot_sdf(name: str, position: List[float]) -> str:
    """Generate SDF for robot (cylinder placeholder)."""
    x, y, z = position
    return f"""<?xml version="1.0" ?>
<sdf version="1.9">
  <model name="{name}">
    <pose>{x} {y} {z} 0 0 0</pose>
    <link name="link">
      <collision name="collision">
        <geometry>
          <cylinder>
            <radius>0.5</radius>
            <length>2.0</length>
          </cylinder>
        </geometry>
      </collision>
      <visual name="visual">
        <geometry>
          <cylinder>
            <radius>0.5</radius>
            <length>2.0</length>
          </cylinder>
        </geometry>
        <material>
          <ambient>1 0 0 1</ambient>
          <diffuse>1 0 0 1</diffuse>
        </material>
      </visual>
      <inertial>
        <mass>1.0</mass>
        <inertia>
          <ixx>0.1</ixx>
          <iyy>0.1</iyy>
          <izz>0.1</izz>
        </inertia>
      </inertial>
    </link>
  </model>
</sdf>"""


def _generate_cube_sdf(name: str, position: List[float]) -> str:
    """Generate SDF for cube object."""
    x, y, z = position
    return f"""<?xml version="1.0" ?>
<sdf version="1.9">
  <model name="{name}">
    <pose>{x} {y} {z} 0 0 0</pose>
    <link name="link">
      <collision name="collision">
        <geometry>
          <box>
            <size>1 1 1</size>
          </box>
        </geometry>
      </collision>
      <visual name="visual">
        <geometry>
          <box>
            <size>1 1 1</size>
          </box>
        </geometry>
        <material>
          <ambient>0 0 1 1</ambient>
          <diffuse>0 0 1 1</diffuse>
        </material>
      </visual>
      <inertial>
        <mass>1.0</mass>
        <inertia>
          <ixx>0.1</ixx>
          <iyy>0.1</iyy>
          <izz>0.1</izz>
        </inertia>
      </inertial>
    </link>
  </model>
</sdf>"""


if __name__ == "__main__":
    import uvicorn
    
    if not GAZEBO_AVAILABLE:
        print("=" * 60)
        print("WARNING: Running in mock mode (Gazebo not available)")
        print("=" * 60)
        print("\nTo install Gazebo Harmonic:")
        print("  1. Install via Conda: conda install libgz-sim8 -c conda-forge")
        print("  2. Install Python bindings: pip install gz-sim8 gz-transport13 gz-math7")
        print("\nSee GAZEBO_INSTALLATION.md for detailed instructions")
        print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8002)
