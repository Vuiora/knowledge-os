"""
Wiki.js API Client

This module provides a Python client for interacting with Wiki.js API,
specifically for triggering Git synchronization and querying sync status.

Requirements: 4.4, 8.2
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)


class WikiJsClient:
    """
    Client for interacting with Wiki.js API.
    
    This client provides methods for:
    - Triggering manual Git synchronization
    - Querying synchronization status
    - Managing Wiki.js storage backend
    
    Requirements: 4.4, 8.2
    """
    
    def __init__(self, base_url: str, api_token: str, timeout: float = 30.0):
        """
        Initialize Wiki.js API client.
        
        Args:
            base_url: Base URL of Wiki.js instance (e.g., "http://wiki:3000")
            api_token: API authentication token
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.timeout = timeout
        
        # Prepare headers for API requests
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"Initialized Wiki.js client for {self.base_url}")
    
    async def trigger_sync(self) -> Dict[str, Any]:
        """
        Trigger manual Git synchronization in Wiki.js.
        
        This method calls the Wiki.js API to trigger an immediate
        synchronization with the configured Git repository.
        
        Requirements: 4.4, 8.2
        
        Returns:
            Dictionary containing:
                - success (bool): Whether sync was triggered successfully
                - message (str): Status message
                - timestamp (str): ISO timestamp of the request
                
        Raises:
            httpx.HTTPError: If the API request fails
        """
        endpoint = f"{self.base_url}/api/storage/sync"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Triggering Wiki.js sync at {endpoint}")
                
                response = await client.post(
                    endpoint,
                    headers=self.headers,
                    json={}
                )
                
                if response.status_code == 200:
                    logger.info("Wiki.js sync triggered successfully")
                    return {
                        "success": True,
                        "message": "Sync triggered successfully",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                elif response.status_code == 401:
                    logger.error("Wiki.js authentication failed - invalid token")
                    return {
                        "success": False,
                        "message": "Authentication failed - invalid API token",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                elif response.status_code == 404:
                    logger.error("Wiki.js sync endpoint not found")
                    return {
                        "success": False,
                        "message": "Sync endpoint not found - check Wiki.js version",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    logger.error(
                        f"Wiki.js sync failed: {response.status_code} - {response.text}"
                    )
                    return {
                        "success": False,
                        "message": f"HTTP {response.status_code}: {response.text}",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
        except httpx.TimeoutException:
            logger.error("Wiki.js sync request timed out")
            return {
                "success": False,
                "message": "Request timed out",
                "timestamp": datetime.utcnow().isoformat()
            }
        except httpx.ConnectError as e:
            logger.error(f"Failed to connect to Wiki.js: {e}")
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Unexpected error triggering Wiki.js sync: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Unexpected error: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_sync_status(self) -> Dict[str, Any]:
        """
        Query the current Git synchronization status from Wiki.js.
        
        This method retrieves information about the last sync operation,
        including timestamp, status, and any error messages.
        
        Requirements: 4.4, 8.2
        
        Returns:
            Dictionary containing:
                - success (bool): Whether status was retrieved successfully
                - last_sync (str): ISO timestamp of last sync (if available)
                - status (str): Current sync status
                - message (str): Status message or error details
                
        Raises:
            httpx.HTTPError: If the API request fails
        """
        endpoint = f"{self.base_url}/api/storage/status"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Querying Wiki.js sync status at {endpoint}")
                
                response = await client.get(
                    endpoint,
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info("Wiki.js sync status retrieved successfully")
                    
                    return {
                        "success": True,
                        "last_sync": data.get("lastSync"),
                        "status": data.get("status", "unknown"),
                        "message": data.get("message", "Status retrieved successfully")
                    }
                elif response.status_code == 401:
                    logger.error("Wiki.js authentication failed - invalid token")
                    return {
                        "success": False,
                        "status": "error",
                        "message": "Authentication failed - invalid API token"
                    }
                elif response.status_code == 404:
                    logger.error("Wiki.js status endpoint not found")
                    return {
                        "success": False,
                        "status": "error",
                        "message": "Status endpoint not found - check Wiki.js version"
                    }
                else:
                    logger.error(
                        f"Failed to get Wiki.js status: {response.status_code} - {response.text}"
                    )
                    return {
                        "success": False,
                        "status": "error",
                        "message": f"HTTP {response.status_code}: {response.text}"
                    }
                    
        except httpx.TimeoutException:
            logger.error("Wiki.js status request timed out")
            return {
                "success": False,
                "status": "error",
                "message": "Request timed out"
            }
        except httpx.ConnectError as e:
            logger.error(f"Failed to connect to Wiki.js: {e}")
            return {
                "success": False,
                "status": "error",
                "message": f"Connection failed: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error getting Wiki.js status: {e}", exc_info=True)
            return {
                "success": False,
                "status": "error",
                "message": f"Unexpected error: {str(e)}"
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check if Wiki.js API is accessible and responding.
        
        Returns:
            Dictionary containing:
                - healthy (bool): Whether Wiki.js is accessible
                - message (str): Status message
        """
        endpoint = f"{self.base_url}/healthz"
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(endpoint)
                
                if response.status_code == 200:
                    return {
                        "healthy": True,
                        "message": "Wiki.js is accessible"
                    }
                else:
                    return {
                        "healthy": False,
                        "message": f"HTTP {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Wiki.js health check failed: {e}")
            return {
                "healthy": False,
                "message": str(e)
            }
