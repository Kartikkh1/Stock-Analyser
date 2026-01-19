"""WebSocket endpoint for stock analysis."""

import asyncio
from typing import Optional, Dict, Any, Callable, Awaitable
from fastapi import WebSocket, WebSocketDisconnect

from backend.services import run_stock_analysis
from stock_analyser.utils.logger import logger


# Type alias for action handlers
ActionHandler = Callable[[Dict[str, Any], WebSocket, Optional[asyncio.Task], Optional[str]], Awaitable[bool]]


async def handle_cancel_action(
    message: Dict[str, Any],
    websocket: WebSocket,
    analysis_task: Optional[asyncio.Task],
    stock_ticker: Optional[str]
) -> bool:
    """
    Handle cancel action from client.
    
    Returns:
        bool: True to stop listening for more messages, False to continue
    """
    logger.info(f"Received cancel request for {stock_ticker or 'unknown'}")
    if analysis_task and not analysis_task.done():
        analysis_task.cancel()
    return True  # Stop listening after cancel


# Action handler registry
ACTION_HANDLERS: Dict[str, ActionHandler] = {
    "cancel": handle_cancel_action,
}


async def listen_for_messages(
    websocket: WebSocket,
    analysis_task: Optional[asyncio.Task] = None,
    stock_ticker: Optional[str] = None
):
    """
    Listen for incoming WebSocket messages and dispatch to appropriate handlers.
    
    This function runs concurrently with the analysis task and listens for
    client messages. It uses a registry pattern to dispatch actions to their
    respective handlers, making it easy to add new event types in the future.
    
    Args:
        websocket: WebSocket connection to receive messages from
        analysis_task: Analysis task to cancel if requested
        stock_ticker: Stock ticker being analyzed (for logging)
    """
    try:
        while True:
            message = await websocket.receive_json()
            action = message.get("action")
            
            if not action:
                logger.warning("Received message without 'action' field")
                continue
            
            # Look up and execute the handler
            handler = ACTION_HANDLERS.get(action)
            
            if handler:
                # Execute the handler and check if we should stop listening
                should_stop = await handler(
                    message, websocket, analysis_task, stock_ticker
                )
                if should_stop:
                    break
            else:
                logger.warning(f"Unknown action received: {action}")
                await websocket.send_json({
                    "error": f"Unknown action: {action}",
                    "available_actions": list(ACTION_HANDLERS.keys())
                })
                
    except WebSocketDisconnect:
        logger.info("Client disconnected")
        if analysis_task and not analysis_task.done():
            analysis_task.cancel()
    except Exception as e:
        logger.error(f"Error in message listener: {e}")


async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time stock analysis with progress updates.
    
    Accepts WebSocket connections, receives analysis requests, and streams
    progress updates back to the client. Supports cancellation via task.cancel().
    
    Args:
        websocket: WebSocket connection
    """
    await websocket.accept()
    analysis_task = None
    
    try:
        # Receive initial request
        data = await websocket.receive_json()
        stock_ticker = data.get("stock_ticker")
        llm_choice = data.get("llm_choice", "openai")
        
        if not stock_ticker:
            await websocket.send_json({"error": "No stock ticker provided"})
            return
        
        # Create analysis task
        analysis_task = asyncio.create_task(
            run_stock_analysis(websocket, stock_ticker, llm_choice)
        )
        
        # Create task to listen for messages (including cancel and future actions)
        listener_task = asyncio.create_task(
            listen_for_messages(websocket, analysis_task, stock_ticker)
        )
        
        # Wait for either analysis to complete or cancellation
        done, pending = await asyncio.wait(
            [analysis_task, listener_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel any pending tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    except WebSocketDisconnect:
        logger.info("Client disconnected from WebSocket")
        if analysis_task and not analysis_task.done():
            analysis_task.cancel()
            try:
                await analysis_task
            except asyncio.CancelledError:
                pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass
