#!/usr/bin/env python
import sys
import warnings
import logging

from datetime import datetime

from stock_analyser.crew import StockAnalyser
from stock_analyser.utils.logger import logger

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the crew.
    """
    logger.info("Starting Stock Analyser application.")

    inputs = {
        'name': 'GOOG', 
        'current_year': str(datetime.now().year)
    }

    # Prompt user for LLM selection
    logger.info("Choose the LLM you want to use for research and reporting:")
    logger.info("1. Anthropic (Claude Sonnet)")
    logger.info("2. Gemini (Gemini 2.5 Flash)")
    logger.info("3. OpenAI (GPT-5)")
    
    llm_selection = input("Enter the number of your chosen LLM (e.g., '1'): ")
    selected_llm_type = 'anthropic' # Default to Anthropic

    if llm_selection == '1':
        selected_llm_type = 'anthropic'
    elif llm_selection == '2':
        selected_llm_type = 'gemini'
    elif llm_selection == '3':
        selected_llm_type = 'openai'
    else:
        logger.warning("Invalid selection. Defaulting to Anthropic.")

    try:
        StockAnalyser(selected_llm_type).crew().kickoff(inputs=inputs)
        logger.info("Stock Analyser crew successfully kicked off.")
    except Exception as e:
        logger.error(f"An error occurred while running the crew: {e}", exc_info=True)
        raise Exception(f"An error occurred while running the crew: {e}")
