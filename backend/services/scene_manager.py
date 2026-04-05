"""
Scene manager service.
Maintains in-memory scene state per session.
"""

from typing import Dict, List, Any, Optional
from threading import RLock


class SceneManager:
    """
    Manages simulation scene state.
    Maintains state per session_id.
    Thread-safe with reentrant locks.
    """
    
    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._lock = RLock()  # Reentrant lock to allow nested calls
    
    def initialize_session(self, session_id: str) -> None:
        """Initialize a new session."""
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = {
                    "current_scene": None,
                    "robots": {},
                    "objects": {}
                }
    
    def get_state(self, session_id: str) -> Dict[str, Any]:
        """Get current scene state."""
        with self._lock:
            self.initialize_session(session_id)
            return dict(self._sessions[session_id])
    
    def apply_actions(
        self,
        session_id: str,
        actions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Apply actions to scene state.
        
        Args:
            session_id: Session identifier
            actions: List of validated actions
            
        Returns:
            Updated scene state
        """
        with self._lock:
            self.initialize_session(session_id)
            state = self._sessions[session_id]
            
            for action in actions:
                action_type = action.get("type")
                
                if action_type == "create_scene":
                    state["current_scene"] = action.get("scene_name", "default")
                    state["robots"] = {}
                    state["objects"] = {}
                
                elif action_type == "spawn_robot":
                    robot_id = action["robot_id"]
                    state["robots"][robot_id] = {
                        "position": action["position"]
                    }
                
                elif action_type == "add_object":
                    object_id = action["object_id"]
                    state["objects"][object_id] = {
                        "position": action["position"]
                    }
                
                elif action_type == "move_object":
                    object_id = action["object_id"]
                    if object_id in state["objects"]:
                        state["objects"][object_id]["position"] = action["position"]
                    elif object_id in state["robots"]:
                        state["robots"][object_id]["position"] = action["position"]
                
                elif action_type == "delete_object":
                    object_id = action["object_id"]
                    if object_id in state["objects"]:
                        del state["objects"][object_id]
                    elif object_id in state["robots"]:
                        del state["robots"][object_id]
            
            return dict(state)
    
    def clear_session(self, session_id: str) -> None:
        """Clear session data."""
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]


def create_scene_manager() -> SceneManager:
    """Factory function to create SceneManager instance."""
    return SceneManager()
