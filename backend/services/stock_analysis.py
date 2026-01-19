"""Stock analysis service for running analysis tasks."""

import asyncio
from datetime import datetime
from dotenv import load_dotenv
from fastapi import WebSocket

from stock_analyser.crew import StockAnalyser
from stock_analyser.utils.logger import logger


async def run_stock_analysis(
    websocket: WebSocket,
    stock_ticker: str,
    llm_choice: str
):
    """
    Run stock analysis asynchronously and send updates via WebSocket.
    
    Args:
        websocket: WebSocket connection to send updates
        stock_ticker: Stock ticker symbol to analyze
        llm_choice: LLM provider choice (openai, anthropic, gemini)
    """
    try:
        # Send initial status
        await websocket.send_json({
            "stock_ticker": stock_ticker,
            "llm_choice": llm_choice,
            "status": "initializing",
            "message": "Initializing stock analysis...",
            "progress": 0
        })
        
        # Load environment variables
        load_dotenv()
        
        # Send status for data gathering phase
        await websocket.send_json({
            "stock_ticker": stock_ticker,
            "status": "researching",
            "message": f"Gathering data for {stock_ticker}...",
            "progress": 10
        })
        
        # Create inputs for the crew
        inputs = {
            'name': stock_ticker,
            'current_year': str(datetime.now().year)
        }
        
        # Send status for analysis phase
        await websocket.send_json({
            "stock_ticker": stock_ticker,
            "status": "analyzing",
            "message": "Running technical analysis...",
            "progress": 30
        })
        
        # Run the analysis in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        
        # Create the crew
        stock_crew = StockAnalyser(llm_choice, stock_name=inputs['name'])
        
        # Send status for sentiment analysis
        await websocket.send_json({
            "stock_ticker": stock_ticker,
            "status": "analyzing",
            "message": "Performing sentiment analysis...",
            "progress": 50
        })
        
        # Run the crew kickoff in a thread pool
        # Note: Thread pool tasks cannot be cancelled directly via task.cancel()
        # Cancellation will occur at the next await point after this executor completes
        result = await loop.run_in_executor(
            None,
            lambda: stock_crew.crew().kickoff(inputs=inputs)
        )
        
        # Send status for report generation
        await websocket.send_json({
            "stock_ticker": stock_ticker,
            "status": "generating_report",
            "message": "Generating final report...",
            "progress": 80
        })
        
        # Read the generated report file
        report_path = f'output/{stock_ticker}_{llm_choice}_report.md'
        try:
            with open(report_path, 'r') as f:
                report_content = f.read()
        except FileNotFoundError:
            report_content = "Report file not found. Analysis may have encountered an issue."
        
        # Send completion status with the report
        await websocket.send_json({
            "stock_ticker": stock_ticker,
            "llm_choice": llm_choice,
            "status": "completed",
            "message": "Analysis complete!",
            "progress": 100,
            "report": report_content,
            "report_path": report_path
        })
        
        logger.info(f"Successfully completed analysis for {stock_ticker}")
        
    except asyncio.CancelledError:
        logger.info(f"Analysis cancelled for {stock_ticker}")
        try:
            await websocket.send_json({
                "stock_ticker": stock_ticker,
                "status": "cancelled",
                "message": "Analysis was cancelled",
                "progress": 0
            })
        except Exception as e:
            logger.debug(f"Could not send cancellation message (connection likely closed): {e}")
    except Exception as e:
        logger.error(f"Error during stock analysis: {e}", exc_info=True)
        await websocket.send_json({
            "stock_ticker": stock_ticker,
            "status": "error",
            "message": f"An error occurred: {str(e)}",
            "error": str(e)
        })
