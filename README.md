# Stock Analysis System

## Project Definition
This project implements a stock analysis system that leverages AI agents to perform comprehensive research and analysis of stock market data. The system aims to provide detailed insights into various aspects of a given stock, including technical indicators, fundamental analysis, and market sentiment.

## How to Run
To run this project, follow these steps:

1.  **Prerequisites:** Ensure you have Python 3.10 or higher installed.

2.  **Install UV (if you haven't already):**

    ```bash
    pip install uv
    ```

3.  **Install Dependencies:**
    Navigate to your project directory and install the dependencies. `uv` will automatically create a virtual environment (`.venv`) if one isn't already active.

    ```bash
    uv sync
    ```

4.  **Environment Variables:**
    Create a `.env` file in the root directory of the project and add your API keys. For example:

    ```
    FINNHUB_API_KEY="your_finnhub_api_key_here"
    OPENAI_API_KEY="your_openai_api_key_here"
    ANTHROPIC_API_KEY="your_anthropic_api_key_here"
    GEMINI_API_KEY="your_gemini_api_key_here"
    ```

5.  **Execute the System:**
    Run the main application script:

    ```bash
    uv run stock_analyser
    ```

## What We Are Doing
The system orchestrates several AI agents, each specializing in a different aspect of stock analysis:

*   **Technical Analyst:** Analyzes historical price data to identify trends, support/resistance levels, and potential trading opportunities using various technical indicators.
*   **Fundamental Analyst:** Assesses a company's financial health and intrinsic value by examining financial statements and key financial ratios.
*   **Sentiment Analyst:** Gathers and interprets public and market sentiment from news, social media, and other sources to understand emotional drivers behind stock movements.
*   **Researcher:** Conducts broad market research to uncover general news, developments, analyst ratings, and other relevant qualitative information.
*   **Reporter:** Compiles the findings from all agents into a comprehensive and detailed stock analysis report.