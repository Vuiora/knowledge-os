"""
Webhook Handler Service for Knowledge System

This service receives webhooks from Gitea and triggers synchronization
across Wiki.js, MkDocs, and AI Assistant services.

Requirements: 8.3, 8.4
"""

import os
import hmac
import hashlib
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
import httpx

from wiki_client import WikiJsClient
from monitoring import ServiceMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Knowledge System Webhook Handler",
    description="Handles webhooks from Gitea and triggers synchronization",
    version="1.0.0"
)

# Configuration from environment variables
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")
WIKI_URL = os.getenv("WIKI_URL", "http://wiki:3000")
WIKI_TOKEN = os.getenv("WIKI_TOKEN", "")
AI_URL = os.getenv("AI_URL", "http://ai-assistant:8000")
MKDOCS_URL = os.getenv("MKDOCS_URL", "http://mkdocs-builder:8080")

# Initialize Wiki.js client
wiki_client = WikiJsClient(base_url=WIKI_URL, api_token=WIKI_TOKEN)

# Initialize service monitor
monitor = ServiceMonitor("webhook-handler")


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify Gitea webhook signature using HMAC-SHA256.
    
    Args:
        payload: Raw request body bytes
        signature: Signature from X-Gitea-Signature header
        secret: Webhook secret
        
    Returns:
        True if signature is valid, False otherwise
    """
    if not secret:
        logger.warning("No webhook secret configured, skipping signature verification")
        return True
    
    if not signature:
        logger.error("No signature provided in request")
        return False
    
    # Compute expected signature
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Compare signatures (constant-time comparison)
    return hmac.compare_digest(signature, expected_signature)


def extract_changed_files(event_data: Dict[str, Any]) -> list[str]:
    """
    Extract list of changed files from Gitea push event.
    
    Args:
        event_data: Gitea webhook payload
        
    Returns:
        List of file paths that were added, modified, or removed
    """
    changed_files = []
    
    # Extract commits from push event
    commits = event_data.get("commits", [])
    
    for commit in commits:
        # Add modified files
        changed_files.extend(commit.get("added", []))
        changed_files.extend(commit.get("modified", []))
        changed_files.extend(commit.get("removed", []))
    
    # Remove duplicates while preserving order
    seen = set()
    unique_files = []
    for file in changed_files:
        if file not in seen:
            seen.add(file)
            unique_files.append(file)
    
    return unique_files


def route_event(event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Route webhook event to appropriate handler based on event type.
    
    Args:
        event_type: Type of Gitea event (e.g., "push")
        event_data: Event payload data
        
    Returns:
        Dictionary with routing results
    """
    logger.info(f"Routing event type: {event_type}")
    
    if event_type == "push":
        return handle_push_event(event_data)
    else:
        logger.warning(f"Unsupported event type: {event_type}")
        return {
            "status": "ignored",
            "message": f"Event type '{event_type}' is not supported"
        }


async def trigger_wiki_sync() -> Dict[str, Any]:
    """
    Trigger Wiki.js synchronization with Git repository.
    
    Requirements: 4.1, 4.4
    
    Returns:
        Dictionary with sync result
    """
    try:
        result = await wiki_client.trigger_sync()
        
        if result["success"]:
            logger.info("Wiki.js sync triggered successfully")
            monitor.record_sync(True, "Wiki sync successful", 0)
            return {
                "service": "wiki",
                "status": "success",
                "message": result["message"],
                "timestamp": result["timestamp"]
            }
        else:
            logger.error(f"Wiki.js sync failed: {result['message']}")
            monitor.record_sync(False, f"Wiki sync failed: {result['message']}", 0)
            return {
                "service": "wiki",
                "status": "error",
                "message": result["message"],
                "timestamp": result["timestamp"]
            }
                
    except Exception as e:
        logger.error(f"Error triggering Wiki.js sync: {e}", exc_info=True)
        monitor.record_sync(False, f"Wiki sync error: {str(e)}", 0)
        monitor.record_error()
        return {
            "service": "wiki",
            "status": "error",
            "message": str(e)
        }


async def trigger_mkdocs_build() -> Dict[str, Any]:
    """
    Trigger MkDocs documentation rebuild.
    
    Requirements: 4.1, 4.4
    
    Returns:
        Dictionary with build result
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            url = f"{MKDOCS_URL}/build"
            
            logger.info(f"Triggering MkDocs build at {url}")
            response = await client.post(url, json={})
            
            if response.status_code == 200:
                logger.info("MkDocs build triggered successfully")
                return {
                    "service": "mkdocs",
                    "status": "success",
                    "message": "Build triggered successfully"
                }
            else:
                logger.error(f"MkDocs build failed: {response.status_code} - {response.text}")
                return {
                    "service": "mkdocs",
                    "status": "error",
                    "message": f"HTTP {response.status_code}: {response.text}"
                }
                
    except httpx.TimeoutException:
        logger.error("MkDocs build request timed out")
        return {
            "service": "mkdocs",
            "status": "error",
            "message": "Request timed out"
        }
    except Exception as e:
        logger.error(f"Error triggering MkDocs build: {e}", exc_info=True)
        return {
            "service": "mkdocs",
            "status": "error",
            "message": str(e)
        }


async def trigger_ai_embedding_update(changed_files: list[str]) -> Dict[str, Any]:
    """
    Trigger AI Assistant to update embeddings for changed files.
    
    Requirements: 6.2
    
    Args:
        changed_files: List of file paths that changed
        
    Returns:
        Dictionary with update result
    """
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            url = f"{AI_URL}/api/update-embeddings"
            payload = {
                "files": changed_files
            }
            
            logger.info(f"Triggering AI embedding update at {url} for {len(changed_files)} files")
            response = await client.post(url, json=payload)
            
            if response.status_code == 200:
                logger.info("AI embedding update triggered successfully")
                monitor.record_sync(True, "AI embedding update successful", len(changed_files))
                return {
                    "service": "ai-assistant",
                    "status": "success",
                    "message": "Embedding update triggered successfully",
                    "files_count": len(changed_files)
                }
            else:
                logger.error(f"AI embedding update failed: {response.status_code} - {response.text}")
                monitor.record_sync(False, f"AI update failed: {response.status_code}", 0)
                return {
                    "service": "ai-assistant",
                    "status": "error",
                    "message": f"HTTP {response.status_code}: {response.text}"
                }
                
    except httpx.TimeoutException:
        logger.error("AI embedding update request timed out")
        monitor.record_sync(False, "AI update timeout", 0)
        monitor.record_error()
        return {
            "service": "ai-assistant",
            "status": "error",
            "message": "Request timed out"
        }
    except Exception as e:
        logger.error(f"Error triggering AI embedding update: {e}", exc_info=True)
        monitor.record_sync(False, f"AI update error: {str(e)}", 0)
        monitor.record_error()
        return {
            "service": "ai-assistant",
            "status": "error",
            "message": str(e)
        }


async def handle_push_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle Git push events by triggering synchronization.
    
    Args:
        event_data: Push event payload
        
    Returns:
        Dictionary with sync results
    """
    # Extract changed files
    changed_files = extract_changed_files(event_data)
    
    logger.info(f"Push event received with {len(changed_files)} changed files")
    logger.debug(f"Changed files: {changed_files}")
    
    # Check if any files in knowledge/ directory were changed
    knowledge_files = [f for f in changed_files if f.startswith("knowledge/")]
    
    if not knowledge_files:
        logger.info("No knowledge files changed, skipping sync")
        return {
            "status": "skipped",
            "message": "No knowledge files were changed",
            "changed_files": changed_files
        }
    
    logger.info(f"Triggering sync for {len(knowledge_files)} knowledge files")
    
    # Trigger all synchronization tasks concurrently
    import asyncio
    wiki_result, mkdocs_result, ai_result = await asyncio.gather(
        trigger_wiki_sync(),
        trigger_mkdocs_build(),
        trigger_ai_embedding_update(knowledge_files),
        return_exceptions=True
    )
    
    # Handle any exceptions from gather
    sync_results = {}
    
    if isinstance(wiki_result, Exception):
        logger.error(f"Wiki sync raised exception: {wiki_result}")
        sync_results["wiki"] = {"status": "error", "message": str(wiki_result)}
    else:
        sync_results["wiki"] = wiki_result
    
    if isinstance(mkdocs_result, Exception):
        logger.error(f"MkDocs build raised exception: {mkdocs_result}")
        sync_results["mkdocs"] = {"status": "error", "message": str(mkdocs_result)}
    else:
        sync_results["mkdocs"] = mkdocs_result
    
    if isinstance(ai_result, Exception):
        logger.error(f"AI embedding update raised exception: {ai_result}")
        sync_results["ai"] = {"status": "error", "message": str(ai_result)}
    else:
        sync_results["ai"] = ai_result
    
    # Determine overall status
    all_success = all(
        result.get("status") == "success" 
        for result in sync_results.values()
    )
    
    return {
        "status": "success" if all_success else "partial",
        "changed_files": knowledge_files,
        "sync_results": sync_results
    }


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "Knowledge System Webhook Handler",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """
    详细健康检查端点
    
    Requirements: 13.3
    """
    # 记录请求
    monitor.record_request()
    
    components = {}
    
    # Check Wiki.js connectivity
    try:
        wiki_health = await wiki_client.health_check()
        components['wiki'] = {
            'status': 'ok' if wiki_health["healthy"] else 'error',
            'url': WIKI_URL,
            'details': wiki_health
        }
    except Exception as e:
        components['wiki'] = {
            'status': 'error',
            'url': WIKI_URL,
            'message': str(e)
        }
    
    # Check AI service connectivity
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{AI_URL}/health")
            components['ai_assistant'] = {
                'status': 'ok' if response.status_code == 200 else 'error',
                'url': AI_URL
            }
    except Exception as e:
        components['ai_assistant'] = {
            'status': 'error',
            'url': AI_URL,
            'message': str(e)
        }
    
    # Check MkDocs service connectivity
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{MKDOCS_URL}/health")
            components['mkdocs'] = {
                'status': 'ok' if response.status_code == 200 else 'error',
                'url': MKDOCS_URL
            }
    except Exception as e:
        components['mkdocs'] = {
            'status': 'error',
            'url': MKDOCS_URL,
            'message': str(e)
        }
    
    # Add configuration status
    components['configuration'] = {
        'status': 'ok',
        'webhook_secret_configured': bool(WEBHOOK_SECRET)
    }
    
    # Get health status from monitor
    health_status = monitor.get_health_status(components)
    
    return health_status.to_dict()


@app.post("/api/wiki/sync")
async def manual_wiki_sync():
    """
    Manually trigger Wiki.js Git synchronization.
    
    This endpoint allows manual triggering of Wiki.js sync
    without requiring a webhook event.
    
    Requirements: 4.4, 8.2
    """
    try:
        result = await wiki_client.trigger_sync()
        
        if result["success"]:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": result["message"],
                    "timestamp": result["timestamp"]
                }
            )
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": result["message"],
                    "timestamp": result["timestamp"]
                }
            )
    except Exception as e:
        logger.error(f"Error in manual sync: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/wiki/status")
async def wiki_sync_status():
    """
    Query Wiki.js Git synchronization status.
    
    Returns information about the last sync operation,
    including timestamp and status.
    
    Requirements: 4.4, 8.2
    """
    # 记录请求
    monitor.record_request()
    
    try:
        result = await wiki_client.get_sync_status()
        
        if result["success"]:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "last_sync": result.get("last_sync"),
                    "sync_status": result.get("status"),
                    "message": result.get("message")
                }
            )
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": result["message"]
                }
            )
    except Exception as e:
        monitor.record_error()
        logger.error(f"Error querying sync status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sync/status")
async def sync_status():
    """
    获取同步状态 API
    
    Requirements: 13.3
    """
    # 记录请求
    monitor.record_request()
    
    try:
        sync_status = monitor.get_sync_status()
        return sync_status.to_dict()
    except Exception as e:
        monitor.record_error()
        logger.error(f"Error getting sync status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sync status: {str(e)}"
        )


@app.get("/api/metrics")
async def system_metrics():
    """
    获取系统指标 API
    
    Requirements: 13.3
    """
    # 记录请求
    monitor.record_request()
    
    try:
        metrics = monitor.get_system_metrics()
        service_stats = monitor.get_service_stats()
        
        return {
            'system': metrics.to_dict(),
            'service': service_stats
        }
    except Exception as e:
        monitor.record_error()
        logger.error(f"Error getting system metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system metrics: {str(e)}"
        )


@app.get("/api/sync/history")
async def sync_history(limit: int = 10):
    """
    获取最近的同步历史
    
    Requirements: 13.3
    """
    # 记录请求
    monitor.record_request()
    
    try:
        history = monitor.get_recent_sync_history(limit=limit)
        return {
            'status': 'ok',
            'history': history,
            'count': len(history)
        }
    except Exception as e:
        monitor.record_error()
        logger.error(f"Error getting sync history: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sync history: {str(e)}"
        )


@app.post("/hooks/knowledge-sync")
async def handle_webhook(
    request: Request,
    x_gitea_signature: Optional[str] = Header(None),
    x_gitea_event: Optional[str] = Header(None)
):
    """
    Main webhook endpoint for Gitea events.
    
    Validates signature and routes events to appropriate handlers.
    
    Requirements: 8.3, 8.4
    """
    # 记录请求
    monitor.record_request()
    
    try:
        # Read raw body for signature verification
        body = await request.body()
        
        # Verify webhook signature
        if not verify_signature(body, x_gitea_signature or "", WEBHOOK_SECRET):
            logger.error("Invalid webhook signature")
            monitor.record_error()
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse JSON payload
        try:
            event_data = await request.json()
        except Exception as e:
            logger.error(f"Failed to parse JSON payload: {e}")
            monitor.record_error()
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        # Get event type
        event_type = x_gitea_event or event_data.get("event_type", "unknown")
        
        # Route event
        result = route_event(event_type, event_data)
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        monitor.record_error()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
