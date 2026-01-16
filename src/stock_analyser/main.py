#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from stock_analyser.crew import StockAnalyser

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the crew.
    """
    inputs = {
        'name': 'GOOG', 
        'current_year': str(datetime.now().year)
    }

    try:
        StockAnalyser().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")
