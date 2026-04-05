"""
Action validation service.
Validates actions against Pydantic schemas.
"""

from typing import List, Dict, Any
from pydantic import ValidationError


class ValidationError(Exception):
    """Custom validation error."""
    pass


class Validator:
    """
    Validates simulation actions.
    Ensures type safety and correctness.
    """
    
    ALLOWED_ACTION_TYPES = {
        "create_scene",
        "spawn_robot",
        "add_object",
        "move_object",
        "delete_object"
    }
    
    def validate_actions(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate a list of actions.
        
        Args:
            actions: List of action dictionaries
            
        Returns:
            Validated actions
            
        Raises:
            ValidationError: If any action is invalid
        """
        validated = []
        
        for i, action in enumerate(actions):
            try:
                validated_action = self.validate_single_action(action)
                validated.append(validated_action)
            except ValidationError as e:
                raise ValidationError(
                    f"Action {i} validation failed: {str(e)}"
                )
        
        return validated
    
    def validate_single_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a single action.
        
        Args:
            action: Action dictionary
            
        Returns:
            Validated action dictionary
            
        Raises:
            ValidationError: If action is invalid
        """
        if not isinstance(action, dict):
            raise ValidationError("Action must be a dictionary")
        
        action_type = action.get("type")
        
        if action_type not in self.ALLOWED_ACTION_TYPES:
            raise ValidationError(
                f"Invalid action type: {action_type}. "
                f"Allowed: {self.ALLOWED_ACTION_TYPES}"
            )
        
        # Validate based on type
        if action_type == "create_scene":
            self._validate_create_scene(action)
        elif action_type == "spawn_robot":
            self._validate_spawn_robot(action)
        elif action_type == "add_object":
            self._validate_add_object(action)
        elif action_type == "move_object":
            self._validate_move_object(action)
        elif action_type == "delete_object":
            self._validate_delete_object(action)
        
        return action
    
    def _validate_create_scene(self, action: Dict[str, Any]) -> None:
        """Validate create_scene action."""
        if "scene_name" not in action:
            raise ValidationError("create_scene requires 'scene_name'")
        
        if not isinstance(action["scene_name"], str):
            raise ValidationError("scene_name must be a string")
        
        if not action["scene_name"].strip():
            raise ValidationError("scene_name cannot be empty")
    
    def _validate_spawn_robot(self, action: Dict[str, Any]) -> None:
        """Validate spawn_robot action."""
        if "robot_id" not in action:
            raise ValidationError("spawn_robot requires 'robot_id'")
        
        if "position" not in action:
            raise ValidationError("spawn_robot requires 'position'")
        
        if not isinstance(action["robot_id"], str):
            raise ValidationError("robot_id must be a string")
        
        self._validate_position(action["position"])
    
    def _validate_add_object(self, action: Dict[str, Any]) -> None:
        """Validate add_object action."""
        if "object_id" not in action:
            raise ValidationError("add_object requires 'object_id'")
        
        if "position" not in action:
            raise ValidationError("add_object requires 'position'")
        
        if not isinstance(action["object_id"], str):
            raise ValidationError("object_id must be a string")
        
        self._validate_position(action["position"])
    
    def _validate_move_object(self, action: Dict[str, Any]) -> None:
        """Validate move_object action."""
        if "object_id" not in action:
            raise ValidationError("move_object requires 'object_id'")
        
        if "position" not in action:
            raise ValidationError("move_object requires 'position'")
        
        if not isinstance(action["object_id"], str):
            raise ValidationError("object_id must be a string")
        
        self._validate_position(action["position"])
    
    def _validate_delete_object(self, action: Dict[str, Any]) -> None:
        """Validate delete_object action."""
        if "object_id" not in action:
            raise ValidationError("delete_object requires 'object_id'")
        
        if not isinstance(action["object_id"], str):
            raise ValidationError("object_id must be a string")
    
    def _validate_position(self, position: Any) -> None:
        """Validate position is [x, y, z]."""
        if not isinstance(position, (list, tuple)):
            raise ValidationError("Position must be a list or tuple")
        
        if len(position) != 3:
            raise ValidationError("Position must have exactly 3 elements")
        
        for i, coord in enumerate(position):
            if not isinstance(coord, (int, float)):
                raise ValidationError(
                    f"Position[{i}] must be numeric, got {type(coord)}"
                )


def create_validator() -> Validator:
    """Factory function to create Validator instance."""
    return Validator()
    validated_actions: list[Any] = []

    for index, action in enumerate(actions):
        if not isinstance(action, dict):
            raise ActionValidationError(f"action at index {index} must be an object")

        action_type = action.get("type")
        if action_type not in ALLOWED_ACTION_TYPES:
            raise ActionValidationError(f"unsupported action type: {action_type}")

        if action_type in {"spawn_robot", "add_object", "move_object"}:
            validate_position(action.get("position"))

        model_cls = ACTION_MODEL_MAP[action_type]
        try:
            validated_actions.append(model_cls.model_validate(action))
        except ValidationError as exc:
            raise ActionValidationError(str(exc)) from exc

    return validated_actions
