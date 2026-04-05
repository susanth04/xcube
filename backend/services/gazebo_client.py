"""
Gazebo Sim HTTP client.
Sends actions to Gazebo Sim server.
Handles retries and error management.
"""

import requests
from typing import Dict, List, Any, Optional
import time
import logging


logger = logging.getLogger(__name__)


class GazeboClientError(Exception):
    """Gazebo client error."""
    pass


class GazeboClient:
    """
    HTTP client for Gazebo Sim server.
    Decoupled from Gazebo - only uses HTTP.
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8002,
        timeout: int = 10,
        max_retries: int = 3
    ):
        """
        Initialize Gazebo client.
        
        Args:
            host: Gazebo server hostname
            port: Gazebo server port
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_url = f"http://{host}:{port}"
    
    def apply_actions(
        self,
        actions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Send actions to Gazebo Sim.
        
        Args:
            actions: List of actions to apply
            
        Returns:
            Response from Gazebo Sim
            
        Raises:
            GazeboClientError: If request fails after retries
        """
        payload = {"actions": actions}
        url = f"{self.base_url}/apply_actions"
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    url,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            
            except requests.exceptions.Timeout:
                logger.warning(
                    f"Gazebo Sim request timeout (attempt {attempt + 1}/"
                    f"{self.max_retries})"
                )
                if attempt == self.max_retries - 1:
                    raise GazeboClientError(
                        f"Gazebo Sim timeout after {self.max_retries} attempts"
                    )
                time.sleep(1)
            
            except requests.exceptions.ConnectionError:
                logger.warning(
                    f"Gazebo Sim connection error (attempt {attempt + 1}/"
                    f"{self.max_retries})"
                )
                if attempt == self.max_retries - 1:
                    raise GazeboClientError(
                        f"Cannot connect to Gazebo Sim at {self.base_url}"
                    )
                time.sleep(1)
            
            except requests.exceptions.RequestException as e:
                logger.error(f"Gazebo Sim request error: {str(e)}")
                raise GazeboClientError(f"Gazebo Sim error: {str(e)}")
        
        raise GazeboClientError("Unknown error")
    
    def health_check(self) -> bool:
        """
        Check Gazebo Sim server health.
        
        Returns:
            True if server is healthy
        """
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Gazebo Sim health check failed: {str(e)}")
            return False


def create_gazebo_client(
    host: str = "localhost",
    port: int = 8002
) -> GazeboClient:
    """Factory function to create GazeboClient instance."""
    return GazeboClient(host=host, port=port)
