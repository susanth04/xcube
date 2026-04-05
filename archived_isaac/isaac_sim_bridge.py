"""
Isaac Sim HTTP server.
Runs inside Isaac Sim Python environment.
Receives actions and applies them to USD stage.

Run inside Isaac Sim with:
    python isaac_server.py
"""

import logging
from typing import Dict, List, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio

# Isaac imports (available inside Isaac Sim environment)
try:
    from omni.isaac.kit import SimulationApp
    from pxr import Usd, UsdGeom, Gf
    ISAAC_AVAILABLE = True
except ImportError:
    ISAAC_AVAILABLE = False
    print("Warning: Isaac imports not available - mock mode active")


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Isaac Sim Server",
    description="Receives and applies simulation actions",
    version="1.0.0"
)


class ActionPayload(BaseModel):
    """Action payload from backend."""
    actions: List[Dict[str, Any]]


# Isaac Sim state
isaac_app = None
stage = None


@app.on_event("startup")
async def startup_event():
    """Initialize Isaac Sim on startup."""
    global isaac_app, stage
    
    if not ISAAC_AVAILABLE:
        logger.warning("Isaac Sim not available - running in mock mode")
        return
    
    try:
        isaac_app = SimulationApp({"headless": False})
        stage = isaac_app.GetStage()
        logger.info("Isaac Sim initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Isaac Sim: {str(e)}")


@app.get("/health")
async def health():
    """Health check."""
    if not ISAAC_AVAILABLE:
        return {"status": "mock_mode", "isaac_available": False}
    
    if isaac_app is None:
        return {"status": "initializing", "isaac_available": False}
    
    return {"status": "ok", "isaac_available": True}


@app.post("/apply_actions")
async def apply_actions(payload: ActionPayload):
    """
    Apply actions to Isaac Sim stage.
    
    Supported actions:
    - create_scene: Create new stage
    - spawn_robot: Load robot USD
    - add_object: Create cube
    - move_object: Set transform
    - delete_object: Remove prim
    
    Args:
        payload: ActionPayload with list of actions
        
    Returns:
        Response with status and results
    """
    if not ISAAC_AVAILABLE:
        logger.warning("Isaac Sim not available - actions not applied")
        return {"status": "mock_mode", "actions_applied": 0}
    
    if stage is None:
        raise HTTPException(status_code=503, detail="Isaac Sim not initialized")
    
    results = []
    
    try:
        for action in payload.actions:
            action_type = action.get("type")
            result = {"action": action_type, "success": False}
            
            try:
                if action_type == "create_scene":
                    _create_scene_action(stage, action)
                    result["success"] = True
                
                elif action_type == "spawn_robot":
                    _spawn_robot_action(stage, action)
                    result["success"] = True
                
                elif action_type == "add_object":
                    _add_object_action(stage, action)
                    result["success"] = True
                
                elif action_type == "move_object":
                    _move_object_action(stage, action)
                    result["success"] = True
                
                elif action_type == "delete_object":
                    _delete_object_action(stage, action)
                    result["success"] = True
                
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


def _create_scene_action(stage: Any, action: Dict[str, Any]) -> None:
    """Create new scene (clear stage)."""
    scene_name = action.get("scene_name", "default")
    
    # Clear all prims
    for prim in stage.GetPrimAtPath("/"):
        if prim.IsValid():
            stage.RemovePrim(prim.GetPath())
    
    # Create default ground plane
    ground_path = f"/World/{scene_name}_ground"
    ground = UsdGeom.Plane.Define(stage, ground_path)
    ground.GetScaleAttr().Set(Gf.Vec3f(100, 100, 1))
    ground.GetDisplayColorAttr().Set([Gf.Vec3f(0.5, 0.5, 0.5)])


def _spawn_robot_action(stage: Any, action: Dict[str, Any]) -> None:
    """Spawn robot by creating a cylinder (placeholder for USD model)."""
    robot_id = action.get("robot_id", "robot")
    position = action.get("position", [0, 0, 0])
    
    robot_path = f"/World/{robot_id}"
    
    # Create cylinder as robot placeholder
    robot = UsdGeom.Cylinder.Define(stage, robot_path)
    robot.GetRadiusAttr().Set(0.5)
    robot.GetHeightAttr().Set(2.0)
    
    # Set position
    robot.AddTransformOp().Set(
        Gf.Matrix4d().SetTranslate(Gf.Vec3d(*position))
    )
    
    # Set color to red
    robot.GetDisplayColorAttr().Set([Gf.Vec3f(1, 0, 0)])


def _add_object_action(stage: Any, action: Dict[str, Any]) -> None:
    """Add cube object to scene."""
    object_id = action.get("object_id", "object")
    position = action.get("position", [0, 0, 0])
    
    object_path = f"/World/{object_id}"
    
    # Create cube
    cube = UsdGeom.Cube.Define(stage, object_path)
    cube.GetSizeAttr().Set(1.0)
    
    # Set position
    cube.AddTransformOp().Set(
        Gf.Matrix4d().SetTranslate(Gf.Vec3d(*position))
    )
    
    # Set color to blue
    cube.GetDisplayColorAttr().Set([Gf.Vec3f(0, 0, 1)])


def _move_object_action(stage: Any, action: Dict[str, Any]) -> None:
    """Move object to new position."""
    object_id = action.get("object_id", "object")
    position = action.get("position", [0, 0, 0])
    
    object_path = f"/World/{object_id}"
    prim = stage.GetPrimAtPath(object_path)
    
    if prim.IsValid():
        # Update transform
        transform_op = prim.GetAttribute("xformOp:transform")
        if transform_op:
            transform_op.Set(
                Gf.Matrix4d().SetTranslate(Gf.Vec3d(*position))
            )


def _delete_object_action(stage: Any, action: Dict[str, Any]) -> None:
    """Delete object from scene."""
    object_id = action.get("object_id", "object")
    object_path = f"/World/{object_id}"
    
    prim = stage.GetPrimAtPath(object_path)
    if prim.IsValid():
        stage.RemovePrim(object_path)


if __name__ == "__main__":
    import uvicorn
    
    if not ISAAC_AVAILABLE:
        print("WARNING: Running in mock mode (Isaac Sim not available)")
        print("This server must run inside Isaac Sim environment")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
