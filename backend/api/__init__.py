"""API routes package."""

from fastapi import APIRouter
from .routes import validation, websocket

# Create main API router
api_router = APIRouter()

# Include route modules
# Note: WebSocket routes are registered differently, so we only include REST routes here
api_router.include_router(validation.router, prefix="/api", tags=["validation"])

__all__ = ["api_router"]
