"""
Mock LLM service.
Deterministically converts prompts to structured actions.
"""

import re
from typing import List, Dict, Any


class MockLLM:
    """
    Deterministic prompt-to-action converter.
    Rules-based mapping with no randomness.
    """
    
    def __init__(self):
        self.action_count = 0
    
    def generate_actions(self, prompt: str) -> List[Dict[str, Any]]:
        """
        Convert natural language prompt to structured actions.
        
        Args:
            prompt: Natural language description
            
        Returns:
            List of action dictionaries
        """
        actions = []
        prompt_lower = prompt.lower()
        
        # Rule 1: Create scene if mentioned
        if any(word in prompt_lower for word in ["create", "new", "warehouse", "scene"]):
            scene_name = self._extract_scene_name(prompt)
            actions.append({
                "type": "create_scene",
                "scene_name": scene_name
            })
        
        # Rule 2: Spawn robots if mentioned
        robot_count = self._count_robots(prompt)
        for i in range(robot_count):
            position = self._extract_position(prompt) if i == 0 else [i, i, 0.5]
            actions.append({
                "type": "spawn_robot",
                "robot_id": f"robot_{i+1}",
                "position": position
            })
        
        # Rule 3: Add objects (shelves, cubes, etc.) if mentioned
        object_count = self._count_objects(prompt)
        for i in range(object_count):
            position = [i * 2, 0, 0]
            actions.append({
                "type": "add_object",
                "object_id": f"object_{i+1}",
                "position": position
            })
        
        # Rule 4: Move objects if instructed
        if "move" in prompt_lower:
            actions.extend(self._parse_move_commands(prompt))
        
        # Rule 5: Delete objects if instructed
        if "delete" in prompt_lower or "remove" in prompt_lower:
            actions.extend(self._parse_delete_commands(prompt))
        
        return actions if actions else [{"type": "create_scene", "scene_name": "default"}]
    
    def _extract_scene_name(self, prompt: str) -> str:
        """Extract scene name from prompt."""
        keywords = ["warehouse", "factory", "lab", "scene", "environment"]
        for keyword in keywords:
            if keyword in prompt.lower():
                return keyword
        return "default_scene"
    
    def _count_robots(self, prompt: str) -> int:
        """Count number of robots mentioned."""
        prompt_lower = prompt.lower()
        if "robot" not in prompt_lower:
            return 0
        
        # Check for explicit numbers
        numbers = re.findall(r'\b(\d+)\s*(?:robot|r2d2|arm)', prompt_lower)
        if numbers:
            return int(numbers[0])
        
        # Check for word numbers
        word_numbers = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
        }
        for word, num in word_numbers.items():
            if f"{word} robot" in prompt_lower or f"{word}robot" in prompt_lower:
                return num
        
        return 1 if "robot" in prompt_lower else 0
    
    def _count_objects(self, prompt: str) -> int:
        """Count number of objects mentioned."""
        prompt_lower = prompt.lower()
        keywords = ["shelf", "cube", "box", "object", "item"]
        
        if not any(kw in prompt_lower for kw in keywords):
            return 0
        
        # Check for explicit numbers
        numbers = re.findall(r'\b(\d+)\s*(?:shelf|cube|box|object)', prompt_lower)
        if numbers:
            return int(numbers[0])
        
        # Check for word numbers
        word_numbers = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
        }
        for word, num in word_numbers.items():
            if any(f"{word} {kw}" in prompt_lower or f"{word}{kw}" in prompt_lower for kw in keywords):
                return num
        
        return 0
    
    def _extract_position(self, prompt: str) -> List[float]:
        """Extract position from prompt."""
        # Look for patterns like "position 5 5 0" or "at 10 20 30"
        pattern = r'(?:position|at|location|coord)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)'
        match = re.search(pattern, prompt.lower())
        
        if match:
            return [float(match.group(1)), float(match.group(2)), float(match.group(3))]
        
        return [0.0, 0.0, 0.5]
    
    def _parse_move_commands(self, prompt: str) -> List[Dict[str, Any]]:
        """Parse move commands from prompt."""
        actions = []
        # Pattern: "move robot_1 to 5 5 0"
        pattern = r'move\s+(\w+)\s+(?:to|@)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)'
        matches = re.findall(pattern, prompt.lower())
        
        for obj_id, x, y, z in matches:
            actions.append({
                "type": "move_object",
                "object_id": obj_id,
                "position": [float(x), float(y), float(z)]
            })
        
        return actions
    
    def _parse_delete_commands(self, prompt: str) -> List[Dict[str, Any]]:
        """Parse delete commands from prompt."""
        actions = []
        # Pattern: "delete object_1" or "remove robot_1"
        pattern = r'(?:delete|remove)\s+(\w+)'
        matches = re.findall(pattern, prompt.lower())
        
        for obj_id in matches:
            actions.append({
                "type": "delete_object",
                "object_id": obj_id
            })
        
        return actions


def create_mock_llm() -> MockLLM:
    """Factory function to create MockLLM instance."""
    return MockLLM()
