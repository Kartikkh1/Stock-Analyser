"""API routes package."""

from fastapi import APIRouter
from .routes import validation

# Create main API router
api_router = APIRouter()

# Include route modules
api_router.include_router(validation.router, prefix="/api", tags=["validation"])

__all__ = ["api_router"]
