"""
Test script to verify the integration of enhanced ATR-based stop loss system 
with the Discord bot. This script simulates a stop loss request to the bot
and verifies that the enhanced stop loss system is properly integrated.
"""

import asyncio
import yfinance as yf
import datetime
from technical_analysis import get_stop_loss_recommendations

async def test_discord_stop_loss_integration():
    """Test the integration of enhanced stop loss with Discord bot"""
    print("Testing enhanced stop loss integration with Discord bot...")
    
    # Test with AAPL PUT option
    ticker = "AAPL"
    print(f"\nTesting with {ticker} PUT option")
    
    # Get current price
    stock = yf.Ticker(ticker)
    current_price = stock.info.get('currentPrice', stock.history(period='1d')['Close'].iloc[-1])
    print(f"Current price: ${current_price:.2f}")
    
    # Set option parameters
    option_type = "put"
    
    # Calculate expiration date (2 weeks from now for swing trade)
    today = datetime.datetime.now().date()
    expiration_date = today + datetime.timedelta(days=14)
    expiration_str = expiration_date.strftime("%Y-%m-%d")
    print(f"Expiration date: {expiration_str}")
    
    # Get stop loss recommendations
    stop_loss_result = get_stop_loss_recommendations(ticker, current_price, option_type, expiration_str)
    
    # Check if enhanced stop loss is included
    if "enhanced" in stop_loss_result:
        print("\nEnhanced stop loss recommendation found:")
        enhanced = stop_loss_result["enhanced"]
        print(f"Pattern: {enhanced.get('pattern', 'N/A')}")
        print(f"Stop level: ${enhanced.get('level', 0):.2f}")
        print(f"Time horizon: {enhanced.get('time_horizon', 'N/A')}")
        if enhanced.get('recommendation'):
            print("\nRecommendation:")
            print(enhanced['recommendation'])
    else:
        print("\nNo enhanced stop loss recommendation found")
    
    # Check primary recommendation
    print("\nPrimary recommendation:")
    if "primary" in stop_loss_result:
        primary = stop_loss_result["primary"]
        print(f"Source: {'Enhanced pattern-based' if primary.get('pattern') else 'Standard technical analysis'}")
        print(f"Stop level: ${primary.get('level', 0):.2f}")
        print(f"Time horizon: {primary.get('time_horizon', 'N/A')}")
        if "candle_close_validated" in stop_loss_result:
            print(f"Candle close validation included: {stop_loss_result['candle_close_validated']}")
            print(f"Requires candle close: {stop_loss_result.get('requires_candle_close', False)}")
    else:
        print("No primary recommendation found")
    
    # Test with no pattern detection
    print("\n\nTesting with ticker that likely has no pattern detection...")
    ticker = "TSLA"
    stock = yf.Ticker(ticker)
    current_price = stock.info.get('currentPrice', stock.history(period='1d')['Close'].iloc[-1])
    print(f"Current price: ${current_price:.2f}")
    
    # Get stop loss recommendations
    stop_loss_result = get_stop_loss_recommendations(ticker, current_price, "call", expiration_str)
    
    # Check if enhanced stop loss is included
    if "enhanced" in stop_loss_result:
        print("\nEnhanced stop loss recommendation found:")
        enhanced = stop_loss_result["enhanced"]
        print(f"Pattern: {enhanced.get('pattern', 'N/A')}")
        print(f"Stop level: ${enhanced.get('level', 0):.2f}")
        print(f"Time horizon: {enhanced.get('time_horizon', 'N/A')}")
    else:
        print("\nNo enhanced stop loss recommendation found (expected)")
        print("Using standard technical analysis instead (fallback)")
        
        if "primary" in stop_loss_result:
            primary = stop_loss_result["primary"]
            print(f"Source: Standard technical analysis")
            print(f"Stop level: ${primary.get('level', 0):.2f}")
            print(f"Time horizon: {primary.get('time_horizon', 'N/A')}")

async def main():
    await test_discord_stop_loss_integration()

if __name__ == "__main__":
    asyncio.run(main())