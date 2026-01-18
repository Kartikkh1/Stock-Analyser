#!/usr/bin/env python
import argparse
import sys
import warnings
import logging

from datetime import datetime

from dotenv import load_dotenv

from stock_analyser.crew import StockAnalyser
from stock_analyser.utils.logger import logger

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run(stock_ticker: str, llm_choice: str):
    """
    Run the crew.
    """
    logger.info("Starting Stock Analyser application.")
    load_dotenv()
    inputs = {
        'name': stock_ticker, 
        'current_year': str(datetime.now().year)
    }

    try:
        StockAnalyser(llm_choice, stock_name=inputs['name']).crew().kickoff(inputs=inputs)
        logger.info("Stock Analyser crew successfully kicked off.")
    except Exception as e:
        logger.error(f"An error occurred while running the crew: {e}", exc_info=True)
        raise Exception(f"An error occurred while running the crew: {e}")
