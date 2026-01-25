# Stock Analysis System

## Project Definition
This project implements an AI-powered stock analysis system with a modern web interface. It leverages AI agents to perform comprehensive research and analysis of stock market data, providing detailed insights into technical indicators, fundamental analysis, and market sentiment through an interactive web application.

## Architecture

### Backend (FastAPI)
- **Modular Structure**: Organized into separate modules for better maintainability
  - `backend/api/routes/` - API endpoints (validation, websocket)
  - `backend/services/` - Business logic (stock analysis)
  - `backend/models/` - Request/response models
  - `backend/core/` - Configuration and utilities
- **WebSocket Support**: Real-time progress updates during analysis
- **LLM Model Mapping**: Automatic mapping of LLM providers to specific models
- **Ticker Validation**: API-based validation using Finnhub

### Frontend (React)
- **Modern UI**: Clean, gradient-based design with animations
- **Real-time Updates**: WebSocket integration for live progress tracking
- **Client-side Validation**: Instant ticker format validation
- **API Validation**: Real-time ticker existence checking
- **Interactive Reports**: Formatted markdown display with download option

## How to Run

### Prerequisites
- Python 3.10 or higher
- Node.js 14+ and npm (for frontend)
- UV package manager

### 1. Install UV (if you haven't already)

```bash
pip3 install uv
```

### 2. Install Dependencies

Navigate to your project directory and install Python dependencies:

```bash
uv sync
```

Install frontend dependencies:

```bash
cd frontend
npm install
cd ..
```

### 3. Environment Variables

Create a `.env` file in the root directory with your API keys:

```env
# Required: Finnhub API for stock data validation
FINNHUB_API_KEY="your_finnhub_api_key_here"

# Required: At least ONE of the following LLM API keys (based on your choice)
OPENAI_API_KEY="your_openai_api_key_here"         # If using OpenAI
ANTHROPIC_API_KEY="your_anthropic_api_key_here"   # If using Anthropic
GEMINI_API_KEY="your_gemini_api_key_here"         # If using Google Gemini

# Optional: Enable test mode for quick testing without LLM API calls
TEST_MODE=false
```

### 4. Run the Application

#### Option A: Web Application (Recommended)

**Start the Backend:**
```bash
fastapi dev app.py
```
The API will be available at `http://localhost:8000`

**Start the Frontend** (in a separate terminal):
```bash
cd frontend
npm start
```
The web app will open at `http://localhost:3000`


## Features

### AI-Powered Analysis
The system orchestrates several specialized AI agents:

- **Technical Analyst**: Analyzes historical price data, identifies trends, support/resistance levels, and trading opportunities
- **Fundamental Analyst**: Assesses financial health and intrinsic value through financial statements and ratios
- **Sentiment Analyst**: Interprets market sentiment from news, social media, and other sources
- **Researcher**: Conducts market research, gathers analyst ratings and relevant information
- **Reporter**: Compiles findings into a comprehensive stock analysis report

### Web Application Features

- **Real-time Progress**: Live updates via WebSocket showing analysis progress
- **Interactive Form**: User-friendly interface for ticker input and LLM selection
- **Validation**: 
  - Client-side format validation for stock tickers
  - API-based existence checking via Finnhub
  - Company information preview
- **LLM Selection**: Choose between OpenAI, Anthropic, or Google models
- **Cancellation Support**: Stop analysis mid-process if needed
- **Report Display**: Formatted markdown rendering with download option

## Things to do (good first contributions)

- [ ] **Add caching for the ticker validation API** (avoid repeated Finnhub calls; cache positive/negative results with a short TTL).
- [ ] **Persist the UI list across refresh** (keep the user’s tickers / recent analyses after page reload; e.g., local storage or backend persistence).
- [ ] **Improve UI design** (layout, typography, spacing, accessibility, and overall polish).
- [ ] **Add interactive reporting & graphs** (visualize trends like price history, moving averages, volume, sentiment over time; make charts part of the report view).

### LLM Model Mapping

The system automatically maps LLM provider choices to specific models (configured in `backend/core/config.py`):

| Provider   | Model                        | Description                    |
|------------|------------------------------|--------------------------------|
| OpenAI     | `gpt-4o`                     | Latest GPT-4 model             |
| Anthropic  | `claude-3-5-sonnet-20240620` | Claude Sonnet 4.5              |
| Google     | `gemini-2.5-pro`             | Google Gemini 2.5 Pro          |

**Note:** This is the single source of truth for LLM configuration. All models are specified in `backend/core/config.py`.

### Test Mode

Enable `TEST_MODE=true` in your `.env` file for quick end-to-end testing:
- Uses a lightweight test crew instead of full analysis
- Completes in ~2-3 seconds
- No LLM API calls (free testing!)
- Perfect for testing WebSocket flow, UI, and cancellation

## API Endpoints

### REST Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `POST /api/validate-ticker` - Validate stock ticker symbol

### WebSocket
- `WS /ws/report` - Real-time stock analysis with progress updates

## Project Structure

```
stock_annalyzer/
├── app.py                         # FastAPI application entry point
├── pyproject.toml                 # Python deps (uv)
├── uv.lock                        # Locked dependency versions
├── README.md                      # Main project docs
├── backend/                       # FastAPI backend modules
│   ├── api/
│   │   └── routes/
│   │       ├── validation.py      # Ticker validation endpoint
│   │       └── websocket.py       # WebSocket handler
│   ├── core/
│   │   └── config.py              # Configuration & initialization
│   ├── models/
│   │   └── requests.py            # Pydantic models
│   ├── services/
│   │   └── stock_analysis.py      # Analysis orchestration
│   ├── test_crew.py               # Lightweight test crew
│   └── README.md
├── src/
│   └── stock_analyser/            # Core analysis package
│       ├── main.py
│       ├── crew.py
│       ├── config/
│       │   ├── agents.yaml
│       │   └── tasks.yaml
│       ├── tools/
│       │   ├── finnhub_tools.py
│       │   ├── technical_analysis_tools.py
│       │   └── visualization_tools.py
│       └── utils/
│           └── logger.py
└── frontend/                      # React frontend (Create React App)
    ├── package.json
    ├── public/
    │   └── index.html
    └── src/
        ├── App.js
        ├── App.css
        ├── components/            # UI components (form, report, etc.)
        ├── hooks/                 # UI hooks (validation, analysis flow)
        └── utils/                 # API + websocket helpers
```