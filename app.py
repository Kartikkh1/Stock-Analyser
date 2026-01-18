
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn
from stock_analyser.main import run as run_analyser

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000", # Assuming React frontend runs on port 3000
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StockAnalyserRequest(BaseModel):
    stock_ticker: str
    llm_choice: str = "openai"

@app.post("/analyze")
async def analyze_stock(request: StockAnalyserRequest):
    try:
        # This will be adapted to use websockets for streaming
        run_analyser(request.stock_ticker, request.llm_choice)
        return {"message": "Stock analysis initiated successfully."}
    except Exception as e:
        return {"error": str(e)}

@app.websocket("/ws/report")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            stock_ticker = data.get("stock_ticker")
            llm_choice = data.get("llm_choice", "openai")
            
            # Here you would integrate your stock analyzer logic.
            # For demonstration, we'll just echo back the received data.
            # In a real scenario, run_analyser would be called, and its output
            # (or parts of it) would be sent back via websocket.send_json.
            
            # Example: Running a simplified analysis and sending back results
            if stock_ticker:
                report_data = {
                    "stock_ticker": stock_ticker,
                    "llm_choice": llm_choice,
                    "status": "Analysis in progress...",
                    "data": f"Simulated report for {stock_ticker} using {llm_choice}"
                }
                await websocket.send_json(report_data)
                
                # In a real application, you'd call run_analyser here and
                # stream its output or final report.
                # run_analyser(stock_ticker, llm_choice)
                
                final_report = {
                    "stock_ticker": stock_ticker,
                    "llm_choice": llm_choice,
                    "status": "Analysis complete",
                    "data": f"Final simulated detailed report for {stock_ticker} using {llm_choice}"
                }
                await websocket.send_json(final_report)

            else:
                await websocket.send_json({"error": "No stock ticker provided"})

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")
        await websocket.send_json({"error": str(e)})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
