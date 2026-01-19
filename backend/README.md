# Backend Structure

This directory contains the refactored FastAPI backend for the Stock Analyzer application.

## Directory Structure

```
backend/
├── __init__.py
├── README.md (this file)
├── api/
│   ├── __init__.py              # Main API router aggregation
│   └── routes/
│       ├── __init__.py
│       ├── validation.py        # Ticker validation endpoint
│       └── websocket.py         # WebSocket endpoint for analysis
├── core/
│   ├── __init__.py
│   └── config.py                # Configuration & initialization
├── models/
│   ├── __init__.py
│   └── requests.py              # Pydantic request models
└── services/
    ├── __init__.py
    └── stock_analysis.py        # Stock analysis orchestration logic
```

## Module Descriptions

### `api/`
Contains all API endpoint definitions.

- **`routes/validation.py`**: REST endpoint for validating stock ticker symbols using Finnhub API
- **`routes/websocket.py`**: WebSocket endpoint for real-time stock analysis with progress updates

### `core/`
Core configuration and initialization.

- **`config.py`**: 
  - Finnhub client initialization
  - CORS origins configuration
  - Environment setup

### `models/`
Pydantic models for request/response validation.

- **`requests.py`**: Request models (e.g., `TickerValidationRequest`)

### `services/`
Business logic and service layer.

- **`stock_analysis.py`**: Orchestrates the stock analysis process, manages WebSocket updates, and handles cancellation

## Main Application

The main `app.py` (in the project root) is now minimal and only:
1. Creates the FastAPI app
2. Configures CORS middleware
3. Registers routes
4. Defines health check endpoints

## Running the Application

From the project root:

```bash
fastapi dev app.py
```

## API Endpoints

- **GET** `/` - Root endpoint (health check)
- **GET** `/health` - Health check endpoint
- **POST** `/api/validate-ticker` - Validate stock ticker symbol
- **WS** `/ws/report` - WebSocket for real-time stock analysis

