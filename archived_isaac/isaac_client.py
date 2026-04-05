"""
Isaac Sim HTTP client.
Sends actions to Isaac Sim server.
Handles retries and error management.
"""

import requests
from typing import Dict, List, Any, Optional
import time
import logging


logger = logging.getLogger(__name__)


class IsaacClientError(Exception):
    """Isaac client error."""
    pass


class IsaacClient:
    """
    HTTP client for Isaac Sim server.
    Decoupled from Isaac - only uses HTTP.
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8001,
        timeout: int = 10,
        max_retries: int = 3
    ):
        """
        Initialize Isaac client.
        
        Args:
            host: Isaac server hostname
            port: Isaac server port
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
        Send actions to Isaac Sim.
        
        Args:
            actions: List of actions to apply
            
        Returns:
            Response from Isaac Sim
            
        Raises:
            IsaacClientError: If request fails after retries
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
                    f"Isaac Sim request timeout (attempt {attempt + 1}/"
                    f"{self.max_retries})"
                )
                if attempt == self.max_retries - 1:
                    raise IsaacClientError(
                        f"Isaac Sim timeout after {self.max_retries} attempts"
                    )
                time.sleep(1)
            
            except requests.exceptions.ConnectionError:
                logger.warning(
                    f"Isaac Sim connection error (attempt {attempt + 1}/"
                    f"{self.max_retries})"
                )
                if attempt == self.max_retries - 1:
                    raise IsaacClientError(
                        f"Cannot connect to Isaac Sim at {self.base_url}"
                    )
                time.sleep(1)
            
            except requests.exceptions.RequestException as e:
                logger.error(f"Isaac Sim request error: {str(e)}")
                raise IsaacClientError(f"Isaac Sim error: {str(e)}")
        
        raise IsaacClientError("Unknown error")
    
    def health_check(self) -> bool:
        """
        Check Isaac Sim server health.
        
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
            logger.warning(f"Isaac Sim health check failed: {str(e)}")
            return False


def create_isaac_client(
    host: str = "localhost",
    port: int = 8001
) -> IsaacClient:
    """Factory function to create IsaacClient instance."""
    return IsaacClient(host=host, port=port)
