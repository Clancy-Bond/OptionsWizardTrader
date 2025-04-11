"""
Test script to verify the contract count detection logic.
"""

import discord_bot

def test_contract_count():
    """Test the contract count detection logic with various inputs."""
    print("\nTesting contract count detection...")
    
    nlp = discord_bot.OptionsBotNLP()
    
    # Test cases for contract count detection
    test_cases = [
        "What will my 15 AAPL $230 call contracts be worth if the stock hits $245?",
        "I have 5 contracts of NVDA $500 calls expiring 4/19, what will they be worth if it goes up by $20?",
        "What's a good stop loss for my 3 TSLA $270 calls?",
        "I need a stop loss for my 7 contracts of AMZN $180 calls expiring next month",
        "Show me what my 10 Google call contracts would be worth at $150",
        "What is the value of my 8 FB puts if the stock drops to $200?",
        "I have 20 MSFT calls expiring on Friday, what's a good stop loss?"
    ]
    
    for test_case in test_cases:
        # Extract information using the NLP module
        info = nlp.extract_info(test_case)
        
        print(f"Test case: '{test_case}'")
        print(f"  Contract count: {info['contract_count']}")
        print(f"  Ticker: {info['ticker']}")
        print(f"  Strike: {info['strike']}")
        print(f"  Option type: {info['option_type']}")
        print("---")

if __name__ == "__main__":
    test_contract_count()