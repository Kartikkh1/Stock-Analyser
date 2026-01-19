"""
Stock Analyzer API - Main Application

A FastAPI application for real-time stock analysis with WebSocket support.
Provides ticker validation and interactive stock analysis reports.
"""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from backend.api import api_router
from backend.api.routes.websocket import websocket_endpoint
from backend.core import get_cors_origins
from stock_analyser.utils.logger import logger

# Create FastAPI application
app = FastAPI(
    title="Stock Analyzer API",
    description="AI-Powered Stock Analysis & Reporting",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

# Register WebSocket route
@app.websocket("/ws/report")
async def websocket_route(websocket: WebSocket):
    """WebSocket endpoint for real-time stock analysis."""
    await websocket_endpoint(websocket)


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "message": "Stock Analyzer API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    logger.info("Starting Stock Analyzer API server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
