"""
Test the unusual options activity output format to verify our fixes
"""

import polygon_integration as polygon

def test_unusual():
    print("\nTesting unusual options activity for TSLA:")
    result = polygon.get_simplified_unusual_activity_summary("TSLA")
    print(result)
    
    print("\nTesting unusual options activity for AAPL:")
    result = polygon.get_simplified_unusual_activity_summary("AAPL")
    print(result)

if __name__ == "__main__":
    test_unusual()