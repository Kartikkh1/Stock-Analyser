
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
        run_analyser(request.stock_ticker, request.llm_choice)
        return {"message": "Stock analysis initiated successfully."}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
