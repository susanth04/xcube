"""
Action schema definitions using Pydantic.
Validates all simulation actions.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class Position(BaseModel):
    """3D position validation."""
    x: float
    y: float
    z: float
    
    def to_list(self) -> List[float]:
        return [self.x, self.y, self.z]


class CreateScene(BaseModel):
    """Create a new scene."""
    type: str = Field("create_scene", frozen=True)
    scene_name: str = Field(..., min_length=1)


class SpawnRobot(BaseModel):
    """Spawn a robot at position."""
    type: str = Field("spawn_robot", frozen=True)
    robot_id: str = Field(..., min_length=1)
    position: List[float] = Field(..., min_length=3, max_length=3)
    
    @field_validator("position")
    @classmethod
    def validate_position(cls, v):
        if not all(isinstance(x, (int, float)) for x in v):
            raise ValueError("Position must contain numeric values")
        return v


class AddObject(BaseModel):
    """Add an object to the scene."""
    type: str = Field("add_object", frozen=True)
    object_id: str = Field(..., min_length=1)
    position: List[float] = Field(..., min_length=3, max_length=3)
    
    @field_validator("position")
    @classmethod
    def validate_position(cls, v):
        if not all(isinstance(x, (int, float)) for x in v):
            raise ValueError("Position must contain numeric values")
        return v


class MoveObject(BaseModel):
    """Move an object to a new position."""
    type: str = Field("move_object", frozen=True)
    object_id: str = Field(..., min_length=1)
    position: List[float] = Field(..., min_length=3, max_length=3)
    
    @field_validator("position")
    @classmethod
    def validate_position(cls, v):
        if not all(isinstance(x, (int, float)) for x in v):
            raise ValueError("Position must contain numeric values")
        return v


class DeleteObject(BaseModel):
    """Delete an object from the scene."""
    type: str = Field("delete_object", frozen=True)
    object_id: str = Field(..., min_length=1)


class ActionRequest(BaseModel):
    """Request for processing a prompt into actions."""
    prompt: str = Field(..., min_length=1)
    session_id: Optional[str] = None


class ActionResponse(BaseModel):
    """Response with processed actions and scene state."""
    prompt: str
    actions: List[dict]
    scene_state: dict
