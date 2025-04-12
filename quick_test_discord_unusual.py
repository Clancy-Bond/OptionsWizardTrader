"""
Quick test for the Discord bot's unusual options activity command
"""
import asyncio
import sys
from polygon_integration import get_simplified_unusual_activity_summary

async def test_unusual_activity():
    """
    Test the unusual options activity function directly
    """
    if len(sys.argv) > 1:
        ticker = sys.argv[1].upper()
    else:
        ticker = "TSLA"  # Use TSLA as default for faster testing
    
    # Test the unusual activity handler directly
    print(f"\n===== TESTING UNUSUAL ACTIVITY FOR {ticker} =====\n")
    
    # Get the unusual activity summary directly from the integration module
    summary = get_simplified_unusual_activity_summary(ticker)
    
    print("\n===== UNUSUAL ACTIVITY OUTPUT =====\n")
    print(summary)
    
    # Check if timestamp is included
    if "occurred at" in summary:
        print("\n✅ Timestamp is properly integrated into the output")
    else:
        print("\n❌ Timestamp is missing from the output")

if __name__ == "__main__":
    asyncio.run(test_unusual_activity())