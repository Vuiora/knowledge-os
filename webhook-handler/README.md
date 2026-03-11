# Webhook Handler Service

This service handles webhooks from Gitea and triggers synchronization across the knowledge system components.

## Features

- **Webhook Signature Verification**: Validates incoming webhooks using HMAC-SHA256
- **Event Routing**: Routes different Gitea events to appropriate handlers
- **Synchronization Triggers**: Automatically triggers:
  - Wiki.js Git synchronization
  - MkDocs documentation rebuild
  - AI Assistant embedding updates

## Requirements

- Python 3.11+
- FastAPI
- httpx
- uvicorn

## Configuration

Set the following environment variables:

```bash
WEBHOOK_SECRET=your_webhook_secret_here
WIKI_URL=http://wiki:3000
WIKI_TOKEN=your_wiki_api_token
AI_URL=http://ai-assistant:8000
MKDOCS_URL=http://mkdocs-builder:8080
```

## API Endpoints

### `GET /`
Health check endpoint.

### `GET /health`
Detailed health check with configuration status and Wiki.js connectivity.

### `POST /hooks/knowledge-sync`
Main webhook endpoint for Gitea events.

**Headers:**
- `X-Gitea-Signature`: HMAC-SHA256 signature of the payload
- `X-Gitea-Event`: Event type (e.g., "push")

**Response:**
```json
{
  "status": "success",
  "changed_files": ["knowledge/01-foundations/example.md"],
  "sync_results": {
    "wiki": {"status": "success", "message": "Sync triggered successfully"},
    "mkdocs": {"status": "success", "message": "Build triggered successfully"},
    "ai": {"status": "success", "message": "Embedding update triggered successfully"}
  }
}
```

### `POST /api/wiki/sync`
Manually trigger Wiki.js Git synchronization.

**Response:**
```json
{
  "status": "success",
  "message": "Sync triggered successfully",
  "timestamp": "2026-03-11T10:30:00.000000"
}
```

### `GET /api/wiki/status`
Query Wiki.js Git synchronization status.

**Response:**
```json
{
  "status": "success",
  "last_sync": "2026-03-11T10:25:00.000000",
  "sync_status": "completed",
  "message": "Status retrieved successfully"
}
```

## Gitea Webhook Configuration

1. Go to your Gitea repository settings
2. Navigate to Webhooks
3. Add a new webhook:
   - **URL**: `http://webhook-handler:9000/hooks/knowledge-sync`
   - **Secret**: Same as `WEBHOOK_SECRET` environment variable
   - **Content Type**: `application/json`
   - **Events**: Select "Push events"

## Docker Deployment

Build and run using Docker Compose:

```bash
docker-compose up -d webhook-handler
```

## Development

Run locally:

```bash
pip install -r requirements.txt
python app.py
```

The service will start on port 9000.

## Logging

The service logs all webhook events and synchronization results. View logs:

```bash
docker-compose logs -f webhook-handler
```

## Requirements Validation

This implementation satisfies:
- **Requirement 8.3**: Webhook-based synchronization triggers
- **Requirement 8.4**: Automatic embedding updates on repository changes
- **Requirement 4.1**: Wiki.js Git synchronization
- **Requirement 4.2**: Git storage backend configuration
- **Requirement 4.4**: Configurable sync intervals (triggered on push)
- **Requirement 6.2**: AI embedding generation for new/modified documents
- **Requirement 8.2**: Manual sync triggering and status querying

## Wiki.js Client Module

The `wiki_client.py` module provides a dedicated Python client for Wiki.js API interactions:

### WikiJsClient Class

```python
from wiki_client import WikiJsClient

# Initialize client
client = WikiJsClient(
    base_url="http://wiki:3000",
    api_token="your_api_token",
    timeout=30.0
)

# Trigger sync
result = await client.trigger_sync()

# Query sync status
status = await client.get_sync_status()

# Health check
health = await client.health_check()
```

### Methods

- `trigger_sync()`: Trigger manual Git synchronization
- `get_sync_status()`: Query current synchronization status
- `health_check()`: Check Wiki.js API accessibility
