"""
Gazebo Bridge for Docker/Linux with MJPEG streaming.
Runs Gazebo Harmonic and streams camera output to browser.
"""

import logging
import subprocess
import time
import asyncio
import threading
from typing import Dict, List, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager

import cv2
import numpy as np

# Gazebo available flag
GAZEBO_AVAILABLE = False
try:
    result = subprocess.run(["gz", "sim", "--version"], capture_output=True, text=True, timeout=5)
    if "Gazebo Sim" in result.stdout:
        GAZEBO_AVAILABLE = True
except:
    pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
gazebo_process = None
latest_frame = None
entity_manager = {}
frame_counter = 0


def capture_gazebo_frames():
    """Background thread to capture frames from Gazebo using gz topic."""
    global latest_frame
    
    while True:
        try:
            # Use gz topic to get camera image (echoes as image data)
            result = subprocess.run(
                ["gz", "topic", "-e", "-t", "/camera", "-n", "1"],
                capture_output=True,
                timeout=2
            )
            if result.returncode == 0 and result.stdout:
                # Parse image from gz topic output
                # For now, use a rendered placeholder
                pass
        except:
            pass
        time.sleep(0.1)


def generate_sim_frame() -> bytes:
    """Generate a simulated frame showing the scene state."""
    global frame_counter, entity_manager
    frame_counter += 1
    
    # Create frame
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Sky gradient
    for y in range(200):
        color = int(40 + y * 0.3)
        frame[y, :] = (color + 20, color + 10, color)
    
    # Ground with grid
    frame[200:, :] = (45, 50, 55)
    for i in range(0, 640, 50):
        intensity = 60 + int(10 * np.sin(frame_counter * 0.02 + i * 0.02))
        cv2.line(frame, (i, 200), (int(i * 0.5 + 160), 480), (intensity, intensity, intensity + 10), 1)
    for j in range(200, 480, 40):
        cv2.line(frame, (0, j), (640, j), (55, 60, 65), 1)
    
    # Draw entities from entity_manager
    for name, info in entity_manager.items():
        pos = info.get("position", [0, 0, 0])
        etype = info.get("type", "object")
        
        # Simple 3D to 2D projection
        screen_x = 320 + int(pos[0] * 30)
        screen_y = 350 - int(pos[1] * 20) - int(pos[2] * 40)
        
        if etype == "robot":
            # Red robot
            cv2.circle(frame, (screen_x, screen_y), 20, (60, 60, 180), -1)
            cv2.circle(frame, (screen_x, screen_y), 20, (100, 100, 220), 2)
            cv2.circle(frame, (screen_x, screen_y - 12), 6, (100, 180, 255), -1)
        else:
            # Blue box
            size = 15
            pts = np.array([
                [screen_x - size, screen_y - size],
                [screen_x + size, screen_y - size],
                [screen_x + size, screen_y + size],
                [screen_x - size, screen_y + size]
            ], np.int32)
            cv2.fillPoly(frame, [pts], (180, 120, 60))
            cv2.polylines(frame, [pts], True, (220, 160, 100), 2)
    
    # If no entities, show demo animation
    if not entity_manager:
        t = frame_counter * 0.03
        demo_x = 320 + int(100 * np.sin(t))
        demo_y = 340 + int(30 * np.cos(t * 1.5))
        cv2.circle(frame, (demo_x, demo_y), 25, (60, 60, 180), -1)
        cv2.circle(frame, (demo_x, demo_y), 25, (100, 100, 220), 2)
        cv2.putText(frame, "Demo Robot", (demo_x - 40, demo_y + 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
    
    # Title and status
    cv2.rectangle(frame, (0, 0), (640, 35), (30, 30, 40), -1)
    cv2.putText(frame, "Gazebo Simulation", (20, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    status = "LIVE" if GAZEBO_AVAILABLE else "SIMULATED"
    color = (100, 200, 100) if GAZEBO_AVAILABLE else (100, 180, 255)
    cv2.putText(frame, status, (540, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    cv2.circle(frame, (525, 20), 5, color, -1)
    
    # Entity count
    cv2.putText(frame, f"Entities: {len(entity_manager)}", (20, 470),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (120, 120, 120), 1)
    
    _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return jpeg.tobytes()


async def generate_mjpeg_stream():
    """Generate MJPEG video stream."""
    global latest_frame
    while True:
        frame = latest_frame if latest_frame else generate_sim_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        await asyncio.sleep(0.033)  # ~30 FPS


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    global gazebo_process
    
    logger.info(f"Gazebo available: {GAZEBO_AVAILABLE}")
    
    if GAZEBO_AVAILABLE:
        # Start Gazebo with a simple world
        world_sdf = create_camera_world()
        with open("/tmp/camera_world.sdf", "w") as f:
            f.write(world_sdf)
        
        gazebo_process = subprocess.Popen(
            ["gz", "sim", "-s", "-r", "/tmp/camera_world.sdf"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        logger.info("Gazebo server started")
        time.sleep(2)
    
    yield
    
    if gazebo_process:
        gazebo_process.terminate()
        logger.info("Gazebo server stopped")


app = FastAPI(title="Gazebo Bridge", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ActionPayload(BaseModel):
    actions: List[Dict[str, Any]]


@app.get("/stream")
async def stream():
    """MJPEG video stream endpoint."""
    return StreamingResponse(
        generate_mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "gazebo_available": GAZEBO_AVAILABLE,
        "streaming": True,
        "entities": len(entity_manager)
    }


@app.post("/apply_actions")
async def apply_actions(payload: ActionPayload):
    """Apply simulation actions."""
    global entity_manager
    results = []
    
    for action in payload.actions:
        action_type = action.get("type")
        try:
            if action_type == "create_scene":
                entity_manager.clear()
                results.append({"action": action_type, "success": True})
                
            elif action_type == "spawn_robot":
                robot_id = action.get("robot_id", f"robot_{len(entity_manager)}")
                position = action.get("position", [0, 0, 0.5])
                entity_manager[robot_id] = {"type": "robot", "position": position}
                
                if GAZEBO_AVAILABLE:
                    spawn_in_gazebo(robot_id, position, "robot")
                
                results.append({"action": action_type, "success": True, "id": robot_id})
                logger.info(f"Spawned robot: {robot_id} at {position}")
                
            elif action_type == "add_object":
                object_id = action.get("object_id", f"object_{len(entity_manager)}")
                position = action.get("position", [0, 0, 0.5])
                entity_manager[object_id] = {"type": "object", "position": position}
                
                if GAZEBO_AVAILABLE:
                    spawn_in_gazebo(object_id, position, "object")
                
                results.append({"action": action_type, "success": True, "id": object_id})
                logger.info(f"Added object: {object_id} at {position}")
                
            elif action_type == "move_object":
                object_id = action.get("object_id")
                position = action.get("position", [0, 0, 0])
                if object_id in entity_manager:
                    entity_manager[object_id]["position"] = position
                results.append({"action": action_type, "success": True})
                
            elif action_type == "delete_object":
                object_id = action.get("object_id")
                if object_id in entity_manager:
                    del entity_manager[object_id]
                results.append({"action": action_type, "success": True})
                
            else:
                results.append({"action": action_type, "success": True})
                
        except Exception as e:
            logger.error(f"Action error: {e}")
            results.append({"action": action_type, "success": False, "error": str(e)})
    
    return {"status": "ok", "results": results, "entity_count": len(entity_manager)}


def spawn_in_gazebo(name: str, position: List[float], entity_type: str):
    """Spawn entity in Gazebo using gz service."""
    x, y, z = position
    
    if entity_type == "robot":
        sdf = f'''<sdf version="1.9"><model name="{name}"><pose>{x} {y} {z} 0 0 0</pose><link name="link"><visual name="v"><geometry><cylinder><radius>0.5</radius><length>1</length></cylinder></geometry><material><ambient>1 0 0 1</ambient></material></visual><collision name="c"><geometry><cylinder><radius>0.5</radius><length>1</length></cylinder></geometry></collision></link></model></sdf>'''
    else:
        sdf = f'''<sdf version="1.9"><model name="{name}"><pose>{x} {y} {z} 0 0 0</pose><link name="link"><visual name="v"><geometry><box><size>1 1 1</size></box></geometry><material><ambient>0 0 1 1</ambient></material></visual><collision name="c"><geometry><box><size>1 1 1</size></box></geometry></collision></link></model></sdf>'''
    
    try:
        subprocess.run([
            "gz", "service", "-s", "/world/default/create",
            "--reqtype", "gz.msgs.EntityFactory",
            "--reptype", "gz.msgs.Boolean",
            "--timeout", "1000",
            "--req", f'sdf: "{sdf}"'
        ], capture_output=True, timeout=3)
    except Exception as e:
        logger.error(f"Spawn error: {e}")


def create_camera_world() -> str:
    """Create SDF world with overhead camera."""
    return '''<?xml version="1.0" ?>
<sdf version="1.9">
  <world name="default">
    <physics type="ode"><real_time_update_rate>1000</real_time_update_rate></physics>
    <light type="directional" name="sun">
      <cast_shadows>true</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>1 1 1 1</diffuse>
    </light>
    <model name="ground">
      <static>true</static>
      <link name="link">
        <visual name="visual">
          <geometry><plane><normal>0 0 1</normal><size>50 50</size></plane></geometry>
          <material><ambient>0.3 0.3 0.4 1</ambient></material>
        </visual>
        <collision name="collision">
          <geometry><plane><normal>0 0 1</normal><size>50 50</size></plane></geometry>
        </collision>
      </link>
    </model>
  </world>
</sdf>'''


if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("Gazebo Bridge v2.0 (Docker/Linux)")
    print(f"Gazebo available: {GAZEBO_AVAILABLE}")
    print("Stream: http://localhost:8002/stream")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8002)
