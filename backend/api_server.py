"""
FastAPI backend for prompt-driven simulation.
Handles chat requests, action generation, validation, and Gazebo Sim integration.
"""

import logging
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.schemas.actions import ActionRequest, ActionResponse
from backend.services.mock_llm import create_mock_llm
from backend.services.validator import create_validator, ValidationError
from backend.services.scene_manager import create_scene_manager
from backend.services.gazebo_client import create_gazebo_client, GazeboClientError


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Prompt-Driven Simulation Backend",
    description="Converts natural language to Gazebo simulation actions",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
llm = create_mock_llm()
validator = create_validator()
scene_manager = create_scene_manager()
gazebo_client = create_gazebo_client(host="localhost", port=8002)


@app.on_event("startup")
async def startup_event():
    """On startup, log initialization."""
    logger.info("Backend initialized")
    logger.info(f"Gazebo Sim connection: {gazebo_client.base_url}")


@app.get("/")
async def health_check():
    """Health check endpoint."""
    gazebo_health = gazebo_client.health_check()
    return {
        "status": "ok",
        "gazebo_connected": gazebo_health
    }


@app.post("/chat", response_model=ActionResponse)
async def chat(request: ActionRequest):
    """
    Process natural language prompt into actions.
    
    1. Generate actions from prompt
    2. Validate actions
    3. Update scene state
    4. Send to Isaac Sim
    5. Return response
    
    Args:
        request: ActionRequest with prompt and session_id
        
    Returns:
        ActionResponse with actions and scene state
    """
    try:
        # Ensure session exists
        session_id = request.session_id or "default"
        scene_manager.initialize_session(session_id)
        
        logger.info(f"Processing prompt: {request.prompt}")
        
        # Step 1: Generate actions from prompt
        actions = llm.generate_actions(request.prompt)
        logger.info(f"Generated {len(actions)} actions")
        
        # Step 2: Validate actions
        validated_actions = validator.validate_actions(actions)
        logger.info("Actions validated successfully")
        
        # Step 3: Update scene state
        scene_state = scene_manager.apply_actions(session_id, validated_actions)
        logger.info(f"Scene state updated for session {session_id}")
        
        # Step 4: Send to Gazebo Sim (non-blocking on failure)
        try:
            gazebo_response = gazebo_client.apply_actions(validated_actions)
            logger.info(f"Gazebo Sim response: {gazebo_response}")
        except GazeboClientError as e:
            logger.warning(f"Gazebo Sim unavailable: {str(e)}")
            # Continue without Gazebo - scene state is still updated
        
        # Step 5: Return response
        return ActionResponse(
            prompt=request.prompt,
            actions=[action for action in validated_actions],
            scene_state=scene_state
        )
    
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/state/{session_id}")
async def get_state(session_id: str):
    """Get current scene state for session."""
    return scene_manager.get_state(session_id)


@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear session data."""
    scene_manager.clear_session(session_id)
    return {"status": "cleared", "session_id": session_id}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
