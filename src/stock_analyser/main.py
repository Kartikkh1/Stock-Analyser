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

    # Prompt user for LLM selection
    print("Choose the LLM you want to use for research and reporting:")
    print("1. Anthropic (Claude Sonnet)")
    print("2. Gemini (Gemini 2.5 Flash)")
    print("3. OpenAI (GPT-5)")
    
    llm_selection = input("Enter the number of your chosen LLM (e.g., '1'): ")
    selected_llm_type = 'anthropic' # Default to Anthropic

    if llm_selection == '1':
        selected_llm_type = 'anthropic'
    elif llm_selection == '2':
        selected_llm_type = 'gemini'
    elif llm_selection == '3':
        selected_llm_type = 'openai'
    else:
        print("Invalid selection. Defaulting to Anthropic.")

    try:
        StockAnalyser(selected_llm_type).crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")
