"""WebSocket endpoint for stock analysis."""

import asyncio
from fastapi import WebSocket, WebSocketDisconnect

from backend.services import run_stock_analysis
from stock_analyser.utils.logger import logger


async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time stock analysis with progress updates.
    
    Accepts WebSocket connections, receives analysis requests, and streams
    progress updates back to the client. Supports cancellation.
    
    Args:
        websocket: WebSocket connection
    """
    await websocket.accept()
    cancel_event = asyncio.Event()
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
            run_stock_analysis(websocket, stock_ticker, llm_choice, cancel_event)
        )
        
        # Create task to listen for messages (including cancel)
        async def listen_for_messages():
            try:
                while True:
                    message = await websocket.receive_json()
                    if message.get("action") == "cancel":
                        logger.info(f"Received cancel request for {stock_ticker}")
                        cancel_event.set()
                        if analysis_task and not analysis_task.done():
                            analysis_task.cancel()
                        break
            except WebSocketDisconnect:
                logger.info("Client disconnected, setting cancel event")
                cancel_event.set()
                if analysis_task and not analysis_task.done():
                    analysis_task.cancel()
            except Exception as e:
                logger.error(f"Error in message listener: {e}")
        
        # Run both tasks concurrently
        listener_task = asyncio.create_task(listen_for_messages())
        
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
        cancel_event.set()
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
