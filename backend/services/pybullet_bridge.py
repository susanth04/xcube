"""
PyBullet Physics Simulation Bridge

Provides a clean, persistent physics simulation interface for the prompt-driven
simulation backend. Maintains a global simulation session with safe action application,
proper object registry, and background stepping loop.
"""

import logging
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

import pybullet as p
import pybullet_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] PyBullet: %(message)s",
)
logger = logging.getLogger(__name__)

# Global simulation state
_client_id: Optional[int] = None
_object_registry: Dict[str, int] = {}  # Maps user_id -> pybullet_body_id
_simulation_lock = threading.Lock()
_stepping_thread: Optional[threading.Thread] = None
_should_step = False

# Simulation constants
GRAVITY = (0, 0, -9.8)
TIMESTEP = 1.0 / 240.0
SIMULATION_STEP_RATE_HZ = 240


def _ensure_client_initialized() -> int:
    """Ensure PyBullet client is initialized, raise if not."""
    global _client_id
    if _client_id is None:
        raise RuntimeError("PyBullet simulation not initialized. Call init_simulation() first.")
    return _client_id


def _stepping_loop() -> None:
    """Background thread that steps the simulation at fixed rate."""
    global _client_id, _should_step
    
    while _should_step:
        with _simulation_lock:
            if _client_id is not None:
                p.stepSimulation(physicsClientId=_client_id)
        
        # Sleep to maintain ~240 Hz stepping rate
        time.sleep(TIMESTEP)


def init_simulation() -> None:
    """
    Initialize PyBullet simulation with GUI mode and persistent session.
    Sets up physics, loads ground plane, and starts background stepping loop.
    """
    global _client_id, _should_step, _stepping_thread, _object_registry
    
    with _simulation_lock:
        if _client_id is not None:
            logger.warning("Simulation already initialized. Skipping re-initialization.")
            return
        
        # Connect to PyBullet in GUI mode
        _client_id = p.connect(p.GUI)
        logger.info("PyBullet GUI client connected (client_id=%d)", _client_id)
        
        # Add search path for URDF files
        p.setAdditionalSearchPath(pybullet_data.getDataPath(), physicsClientId=_client_id)
        
        # Configure physics engine
        p.setGravity(*GRAVITY, physicsClientId=_client_id)
        p.setPhysicsEngineParameter(fixedTimeStep=TIMESTEP, physicsClientId=_client_id)
        logger.info("Physics configured: gravity=%s, timestep=%.6f", GRAVITY, TIMESTEP)
        
        # Load ground plane
        ground_id = p.loadURDF("plane.urdf", physicsClientId=_client_id)
        _object_registry["__ground__"] = ground_id
        logger.info("Ground plane loaded (body_id=%d)", ground_id)
        
        # Clear any existing objects
        _object_registry.clear()
        _object_registry["__ground__"] = ground_id
        
        # Start background stepping thread
        _should_step = True
        _stepping_thread = threading.Thread(target=_stepping_loop, daemon=True)
        _stepping_thread.start()
        logger.info("Background stepping loop started")


def shutdown_simulation() -> None:
    """
    Safely shutdown the simulation and background thread.
    Disconnects from PyBullet and cleans up resources.
    """
    global _client_id, _should_step, _stepping_thread, _object_registry
    
    with _simulation_lock:
        if _client_id is None:
            logger.warning("Simulation not initialized. Nothing to shutdown.")
            return
        
        # Stop stepping thread
        _should_step = False
        logger.info("Stepping loop stopped")
        
        # Disconnect PyBullet
        p.disconnect(physicsClientId=_client_id)
        logger.info("PyBullet client disconnected")
        
        # Clear state
        _client_id = None
        _object_registry.clear()
        
        # Wait for thread to finish
        if _stepping_thread is not None and _stepping_thread.is_alive():
            _stepping_thread.join(timeout=2.0)
            logger.info("Stepping thread joined")


def reset_scene() -> None:
    """
    Reset simulation to clean state.
    Removes all objects except ground plane and reloads physics configuration.
    """
    client_id = _ensure_client_initialized()
    
    with _simulation_lock:
        # Remove all objects except ground
        bodies_to_remove = [
            (user_id, body_id)
            for user_id, body_id in _object_registry.items()
            if user_id != "__ground__"
        ]
        
        for user_id, body_id in bodies_to_remove:
            try:
                p.removeBody(body_id, physicsClientId=client_id)
                del _object_registry[user_id]
                logger.info("Removed object '%s' (body_id=%d)", user_id, body_id)
            except Exception as exc:
                logger.warning("Failed to remove body %d: %s", body_id, exc)
        
        # Reconfigure physics (gravity often resets)
        p.setGravity(*GRAVITY, physicsClientId=client_id)
        logger.info("Scene reset. Gravity reconfigured.")


def apply_actions(actions: List[Dict[str, Any]]) -> None:
    """
    Apply a list of simulation actions to the physics environment.
    
    Supported action types:
    - create_scene: Reset simulation
    - spawn_robot: Load robot URDF at position
    - add_object: Load object URDF at position
    - move_object: Move existing object to new position
    - delete_object: Remove object from scene
    
    Args:
        actions: List of action dictionaries with 'type' key
    
    Raises:
        ValueError: If action type is unsupported or parameters invalid
    """
    client_id = _ensure_client_initialized()
    
    if not actions:
        return
    
    logger.info("Applying %d action(s)", len(actions))
    
    with _simulation_lock:
        for i, action in enumerate(actions):
            try:
                action_type = action.get("type")
                
                if action_type == "create_scene":
                    _handle_create_scene(client_id, action, i)
                
                elif action_type == "spawn_robot":
                    _handle_spawn_robot(client_id, action, i)
                
                elif action_type == "add_object":
                    _handle_add_object(client_id, action, i)
                
                elif action_type == "move_object":
                    _handle_move_object(client_id, action, i)
                
                elif action_type == "delete_object":
                    _handle_delete_object(client_id, action, i)
                
                else:
                    raise ValueError(f"Unsupported action type: {action_type}")
            
            except Exception as exc:
                logger.error("Action [%d] failed: %s", i, exc)
                raise


def _handle_create_scene(client_id: int, action: Dict[str, Any], action_index: int) -> None:
    """Handle create_scene action."""
    scene_name = action.get("scene_name", "default_scene")
    logger.info("Action [%d] CREATE_SCENE: '%s'", action_index, scene_name)
    reset_scene()


def _handle_spawn_robot(client_id: int, action: Dict[str, Any], action_index: int) -> None:
    """Handle spawn_robot action."""
    robot_id = action.get("robot_id")
    position = action.get("position", [0, 0, 1])
    
    if not robot_id:
        raise ValueError("spawn_robot requires 'robot_id'")
    
    if robot_id in _object_registry and _object_registry[robot_id] != _object_registry.get("__ground__"):
        logger.warning("Robot '%s' already exists. Skipping.", robot_id)
        return
    
    if len(position) != 3:
        raise ValueError(f"position must be [x, y, z], got {position}")
    
    try:
        # Load robot URDF
        body_id = p.loadURDF(
            "r2d2.urdf",
            basePosition=position,
            physicsClientId=client_id,
        )
        _object_registry[robot_id] = body_id
        logger.info("Action [%d] SPAWN_ROBOT: '%s' at %s (body_id=%d)", 
                   action_index, robot_id, position, body_id)
    except Exception as exc:
        raise RuntimeError(f"Failed to load robot URDF 'r2d2.urdf': {exc}") from exc


def _handle_add_object(client_id: int, action: Dict[str, Any], action_index: int) -> None:
    """Handle add_object action."""
    object_id = action.get("object_id")
    position = action.get("position", [0, 0, 0.5])
    
    if not object_id:
        raise ValueError("add_object requires 'object_id'")
    
    if object_id in _object_registry and _object_registry[object_id] != _object_registry.get("__ground__"):
        logger.warning("Object '%s' already exists. Skipping.", object_id)
        return
    
    if len(position) != 3:
        raise ValueError(f"position must be [x, y, z], got {position}")
    
    try:
        # Load object URDF
        body_id = p.loadURDF(
            "cube_small.urdf",
            basePosition=position,
            physicsClientId=client_id,
        )
        _object_registry[object_id] = body_id
        logger.info("Action [%d] ADD_OBJECT: '%s' at %s (body_id=%d)", 
                   action_index, object_id, position, body_id)
    except Exception as exc:
        raise RuntimeError(f"Failed to load object URDF 'cube_small.urdf': {exc}") from exc


def _handle_move_object(client_id: int, action: Dict[str, Any], action_index: int) -> None:
    """Handle move_object action."""
    object_id = action.get("object_id")
    position = action.get("position", [0, 0, 0.5])
    
    if not object_id:
        raise ValueError("move_object requires 'object_id'")
    
    if object_id not in _object_registry:
        raise ValueError(f"Object '{object_id}' not found in registry")
    
    if len(position) != 3:
        raise ValueError(f"position must be [x, y, z], got {position}")
    
    body_id = _object_registry[object_id]
    
    try:
        # Get current orientation to preserve it
        current_state = p.getBasePositionAndOrientation(body_id, physicsClientId=client_id)
        current_orientation = current_state[1]  # [x, y, z, w] quaternion
        
        # Move object, preserving orientation
        p.resetBasePositionAndOrientation(
            body_id,
            position,
            current_orientation,
            physicsClientId=client_id,
        )
        logger.info("Action [%d] MOVE_OBJECT: '%s' to %s (body_id=%d)", 
                   action_index, object_id, position, body_id)
    except Exception as exc:
        raise RuntimeError(f"Failed to move object '{object_id}': {exc}") from exc


def _handle_delete_object(client_id: int, action: Dict[str, Any], action_index: int) -> None:
    """Handle delete_object action."""
    object_id = action.get("object_id")
    
    if not object_id:
        raise ValueError("delete_object requires 'object_id'")
    
    if object_id not in _object_registry:
        logger.warning("Object '%s' not found in registry. Skipping delete.", object_id)
        return
    
    body_id = _object_registry[object_id]
    
    # Prevent deletion of ground plane
    if object_id == "__ground__":
        logger.warning("Cannot delete ground plane. Skipping.")
        return
    
    try:
        p.removeBody(body_id, physicsClientId=client_id)
        del _object_registry[object_id]
        logger.info("Action [%d] DELETE_OBJECT: '%s' (body_id=%d)", 
                   action_index, object_id, body_id)
    except Exception as exc:
        raise RuntimeError(f"Failed to delete object '{object_id}': {exc}") from exc


def get_object_registry() -> Dict[str, int]:
    """
    Get a copy of the current object registry.
    Maps user object IDs to PyBullet body IDs.
    """
    with _simulation_lock:
        return dict(_object_registry)


def get_object_state(object_id: str) -> Optional[Tuple[List[float], List[float]]]:
    """
    Get current position and orientation of an object.
    
    Args:
        object_id: User-provided object identifier
    
    Returns:
        Tuple of (position, orientation) or None if object not found
    """
    client_id = _ensure_client_initialized()
    
    with _simulation_lock:
        if object_id not in _object_registry:
            return None
        
        body_id = _object_registry[object_id]
        try:
            pos, orn = p.getBasePositionAndOrientation(body_id, physicsClientId=client_id)
            return (list(pos), list(orn))
        except Exception as exc:
            logger.warning("Failed to query state of '%s': %s", object_id, exc)
            return None


# ============================================================================
# Demo and Testing
# ============================================================================

if __name__ == "__main__":
    """
    Demonstration of PyBullet bridge with all supported actions.
    """
    print("\n" + "=" * 70)
    print("PyBullet Bridge Demo")
    print("=" * 70 + "\n")
    
    try:
        # Initialize simulation
        print("[1] Initializing simulation...")
        init_simulation()
        time.sleep(1)
        
        # Create scene
        print("\n[2] Creating scene...")
        apply_actions([
            {"type": "create_scene", "scene_name": "warehouse"}
        ])
        time.sleep(1)
        
        # Spawn robot
        print("\n[3] Spawning robot...")
        apply_actions([
            {"type": "spawn_robot", "robot_id": "robot_1", "position": [0, 0, 0.5]}
        ])
        time.sleep(1)
        
        # Add objects
        print("\n[4] Adding objects...")
        apply_actions([
            {"type": "add_object", "object_id": "cube_1", "position": [1, 0, 0.5]},
            {"type": "add_object", "object_id": "cube_2", "position": [2, 0, 0.5]},
            {"type": "add_object", "object_id": "cube_3", "position": [3, 0, 0.5]},
        ])
        time.sleep(1)
        
        # Move object
        print("\n[5] Moving object...")
        apply_actions([
            {"type": "move_object", "object_id": "cube_1", "position": [0, 2, 1.5]}
        ])
        time.sleep(1)
        
        # Delete object
        print("\n[6] Deleting object...")
        apply_actions([
            {"type": "delete_object", "object_id": "cube_3"}
        ])
        time.sleep(1)
        
        # Print final registry
        print("\n[7] Final object registry:")
        registry = get_object_registry()
        for uid, bid in registry.items():
            state = get_object_state(uid)
            if state:
                pos, orn = state
                print(f"  {uid:15s} -> body_id={bid:3d}, pos={pos}")
            else:
                print(f"  {uid:15s} -> body_id={bid:3d}")
        
        # Keep simulation running for visualization
        print("\n[8] Simulation running in GUI. Close window to exit...")
        print("=" * 70 + "\n")
        
        while True:
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n\nShutdown requested by user.")
    
    except Exception as exc:
        print(f"\n❌ Error: {exc}")
    
    finally:
        print("\nShutting down simulation...")
        shutdown_simulation()
        print("✅ Demo complete.")
