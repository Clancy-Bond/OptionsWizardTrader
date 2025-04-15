"""
Replace the `get_simplified_unusual_activity_summary` function in polygon_integration.py
to properly use dynamic moneyness detection for options
"""

def run_test_query():
    """
    Run a test query to demonstrate dynamic moneyness detection
    """
    from polygon_integration import get_simplified_unusual_activity_summary
    
    print("Testing NVDA unusual options activity with dynamic moneyness detection:")
    result = get_simplified_unusual_activity_summary("NVDA")
    print(result)
    
    print("\nTesting AAPL unusual options activity with dynamic moneyness detection:")
    result = get_simplified_unusual_activity_summary("AAPL")
    print(result)
    
if __name__ == "__main__":
    run_test_query()