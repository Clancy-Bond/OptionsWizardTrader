"""
End-to-end verification script for buffer enforcement.
This script traces through the entire flow from technical analysis to final display
to ensure buffers are only enforced when technical levels exceed limits.
"""
import importlib.util
import sys
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np

# Import technical_analysis.py and discord_bot.py
def import_module_from_file(file_path, module_name):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Import our modules
discord_bot = import_module_from_file("discord_bot.py", "discord_bot")
technical_analysis = import_module_from_file("technical_analysis.py", "technical_analysis")

# Create a mock message class for testing
class MockMessage:
    def __init__(self, content):
        self.content = content
        self.mentions = []

    async def reply(self, content=None, embed=None):
        if embed:
            # Print the embed title and description
            print(f"EMBED TITLE: {embed.title}")
            print(f"EMBED DESCRIPTION: {embed.description}")
            
            # Print all fields
            for field in embed.fields:
                print(f"FIELD: {field.name}")
                print(f"VALUE: {field.value}")
                print("-" * 40)
                
            # Print footer if exists
            if hasattr(embed, '_footer'):
                print(f"FOOTER: {embed._footer.get('text', '')}")
        else:
            print(f"REPLY: {content}")
        return None

def setup_test_case(ticker, current_price, option_type, days_to_expiration):
    """Setup a test case with specific parameters"""
    # Calculate expiration date
    today = datetime.now().date()
    expiration_date = (today + timedelta(days=days_to_expiration)).strftime("%Y-%m-%d")
    
    # Create info dictionary similar to what NLP would extract
    info = {
        'ticker': ticker,
        'option_type': option_type,
        'strike_price': current_price,  # Use current price as strike for simplicity
        'expiration_date': expiration_date,
        'request_type': 'stop_loss'
    }
    
    # Create message
    message_content = f"What's a good stop loss for my {ticker} ${current_price} {option_type}s expiring {expiration_date}?"
    message = MockMessage(message_content)
    
    # Create returns structure
    returns = {
        'ticker': ticker,
        'current_price': current_price,
        'option_type': option_type,
        'days_to_expiration': days_to_expiration,
        'info': info,
        'message': message
    }
    
    return returns

class MockStock:
    """Mock stock class to simulate yfinance for testing"""
    def __init__(self, ticker, current_price):
        self.ticker = ticker
        self.current_price = current_price
        self.info = {'currentPrice': current_price}
    
    def history(self, period=None, interval=None):
        """Return mock history data"""
        # Create a simple DataFrame with price data
        dates = pd.date_range(end=datetime.now(), periods=20)
        
        # Create price data with slight variations
        price_range = self.current_price * 0.05  # 5% range
        open_prices = np.random.uniform(self.current_price - price_range, 
                                        self.current_price + price_range, 
                                        size=len(dates))
        high_prices = open_prices * np.random.uniform(1.0, 1.03, size=len(dates))
        low_prices = open_prices * np.random.uniform(0.97, 1.0, size=len(dates))
        close_prices = np.random.uniform(low_prices, high_prices)
        volume = np.random.randint(100000, 1000000, size=len(dates))
        
        # Create the DataFrame
        df = pd.DataFrame({
            'Open': open_prices,
            'High': high_prices,
            'Low': low_prices,
            'Close': close_prices,
            'Volume': volume
        }, index=dates)
        
        return df

async def test_technical_stop_flow(ticker, current_price, option_type, days_to_expiration, technical_percentage, expect_enforcement=False):
    """
    Test the entire flow from technical analysis to final display with a defined technical level
    
    Args:
        ticker: Stock ticker
        current_price: Current stock price
        option_type: 'call' or 'put'
        days_to_expiration: DTE value
        technical_percentage: The technical level as a percentage from current price
        expect_enforcement: Whether we expect buffer enforcement to happen
    """
    print(f"\n{'='*20} TESTING {ticker} {option_type.upper()} WITH {days_to_expiration} DTE {'='*20}")
    print(f"Current price: ${current_price:.2f}")
    
    # DTE-based buffer limit
    if days_to_expiration <= 1:
        buffer_limit = 1.0
    elif days_to_expiration <= 2:
        buffer_limit = 2.0
    elif days_to_expiration <= 5:
        buffer_limit = 3.0
    elif days_to_expiration <= 60:
        buffer_limit = 5.0
    else:
        buffer_limit = 7.0 if option_type.lower() == 'put' else 5.0
    
    print(f"Buffer limit for {days_to_expiration} DTE: {buffer_limit:.1f}%")
    
    # Calculate the technical stop price
    if option_type.lower() == 'call':
        technical_stop = current_price * (1 - technical_percentage/100)
        buffer_stop = current_price * (1 - buffer_limit/100)
        print(f"Technical stop: ${technical_stop:.2f} ({technical_percentage:.2f}% below current price)")
        print(f"Buffer limit stop: ${buffer_stop:.2f} ({buffer_limit:.2f}% below current price)")
    else:
        technical_stop = current_price * (1 + technical_percentage/100)
        buffer_stop = current_price * (1 + buffer_limit/100)
        print(f"Technical stop: ${technical_stop:.2f} ({technical_percentage:.2f}% above current price)")
        print(f"Buffer limit stop: ${buffer_stop:.2f} ({buffer_limit:.2f}% above current price)")
    
    # Setup test case
    test_case = setup_test_case(ticker, current_price, option_type, days_to_expiration)
    
    # Create bot instance
    bot = discord_bot.OptionsBot()
    
    # Before calling handle_stop_loss_request, we'll inject our mocked technical analysis
    # This is where we'll simulate different technical levels
    orig_get_swing_stop_loss = technical_analysis.get_swing_stop_loss
    
    def mock_get_swing_stop_loss(stock, current_price, option_type, days_to_expiration=None, trade_type=None):
        """Mock get_swing_stop_loss to return our predefined technical level"""
        print(f"MOCK: Creating swing stop loss at technical level: ${technical_stop:.2f}")
        
        if option_type.lower() == 'call':
            direction = "below"
        else:
            direction = "above"
            
        return {
            "level": technical_stop,
            "recommendation": f"📈 **SWING TRADE STOP LOSS (4h-chart)** 📈\n\n• Stock Price Stop Level: ${technical_stop:.2f} ({technical_percentage:.1f}% {direction} current price)\n• Based on key technical support zone with volatility analysis",
            "time_horizon": "swing", 
            "option_stop_price": current_price * 0.5  # Simplified estimation
        }
    
    # Apply our mock function
    technical_analysis.get_swing_stop_loss = mock_get_swing_stop_loss
    
    # Mock get_stop_loss_recommendations
    orig_get_stop_loss_recommendations = technical_analysis.get_stop_loss_recommendations
    
    def mock_get_stop_loss_recommendations(ticker, current_price, option_type, expiration_date=None, trade_type=None):
        """Mock get_stop_loss_recommendations to use our mocked swing_stop_loss"""
        print(f"MOCK: Calling get_stop_loss_recommendations for {ticker} at ${current_price:.2f}")
        
        # Calculate days to expiration
        exp_date = datetime.strptime(expiration_date, "%Y-%m-%d").date()
        today = datetime.now().date()
        days_to_exp = (exp_date - today).days
        
        print(f"MOCK: Days to expiration: {days_to_exp}")
        
        # Create a mock stock
        stock = MockStock(ticker, current_price)
        
        # For simplicity, always return swing for this test
        # This is the method we've mocked above
        swing_result = mock_get_swing_stop_loss(stock, current_price, option_type, days_to_exp, trade_type)
        
        # Return the result with trade_horizon set
        return {
            "trade_horizon": "swing",
            "swing": swing_result,
            "primary": "swing"
        }
    
    # Apply our mock function
    technical_analysis.get_stop_loss_recommendations = mock_get_stop_loss_recommendations
    
    try:
        # Call handle_stop_loss_request
        print("\nCALLING: handle_stop_loss_request")
        response = await bot.handle_stop_loss_request(test_case['message'], test_case['info'])
        
        # Check what the final embed contains to verify the buffer enforcement behavior
        if hasattr(response, 'fields'):
            for field in response.fields:
                if "Stock Price Stop Level:" in field.value:
                    # Extract the final stop loss value and percentage from the embed field
                    import re
                    stop_value_match = re.search(r'\$(\d+\.\d+)', field.value)
                    percentage_match = re.search(r'(\d+\.\d+)%', field.value)
                    
                    if stop_value_match and percentage_match:
                        final_stop = float(stop_value_match.group(1))
                        final_percentage = float(percentage_match.group(1))
                        
                        print(f"\nFINAL DISPLAY: Stop Level: ${final_stop:.2f} ({final_percentage:.1f}%)")
                        
                        # Determine if buffer was enforced by checking final values
                        if option_type.lower() == 'call':
                            if abs(final_stop - buffer_stop) < 0.01:  # Close to buffer stop
                                print(f"DETECTED: Buffer enforced - using max buffer of {buffer_limit:.1f}%")
                                
                                if not expect_enforcement:
                                    print("ERROR: Buffer was enforced but shouldn't have been!")
                                else:
                                    print("SUCCESS: Buffer was enforced as expected")
                            else:
                                print(f"DETECTED: Using technical level of {technical_percentage:.1f}%")
                                
                                if expect_enforcement:
                                    print("ERROR: Buffer should have been enforced but wasn't!")
                                else:
                                    print("SUCCESS: Technical level was used as expected")
                        else:  # PUT option
                            if abs(final_stop - buffer_stop) < 0.01:  # Close to buffer stop
                                print(f"DETECTED: Buffer enforced - using max buffer of {buffer_limit:.1f}%")
                                
                                if not expect_enforcement:
                                    print("ERROR: Buffer was enforced but shouldn't have been!")
                                else:
                                    print("SUCCESS: Buffer was enforced as expected")
                            else:
                                print(f"DETECTED: Using technical level of {technical_percentage:.1f}%")
                                
                                if expect_enforcement:
                                    print("ERROR: Buffer should have been enforced but wasn't!")
                                else:
                                    print("SUCCESS: Technical level was used as expected")
    finally:
        # Restore original functions
        technical_analysis.get_swing_stop_loss = orig_get_swing_stop_loss
        technical_analysis.get_stop_loss_recommendations = orig_get_stop_loss_recommendations

async def run_tests():
    """Run a series of tests with different parameters"""
    # Test cases structure: (ticker, price, option_type, DTE, technical_level, expect_enforcement)
    
    # 1. CALL OPTIONS - Technical levels within buffer limits (shouldn't enforce)
    await test_technical_stop_flow('AAPL', 200.0, 'call', 1, 0.5, expect_enforcement=False)  # 0.5% within 1% limit
    await test_technical_stop_flow('MSFT', 400.0, 'call', 2, 1.8, expect_enforcement=False)  # 1.8% within 2% limit
    await test_technical_stop_flow('TSLA', 250.0, 'call', 5, 2.9, expect_enforcement=False)  # 2.9% within 3% limit
    await test_technical_stop_flow('GOOG', 180.0, 'call', 30, 4.8, expect_enforcement=False)  # 4.8% within 5% limit
    
    # 2. CALL OPTIONS - Technical levels exceeding buffer limits (should enforce)
    await test_technical_stop_flow('AAPL', 200.0, 'call', 1, 1.5, expect_enforcement=True)  # 1.5% exceeds 1% limit
    await test_technical_stop_flow('MSFT', 400.0, 'call', 2, 2.5, expect_enforcement=True)  # 2.5% exceeds 2% limit
    await test_technical_stop_flow('TSLA', 250.0, 'call', 5, 3.5, expect_enforcement=True)  # 3.5% exceeds 3% limit
    await test_technical_stop_flow('GOOG', 180.0, 'call', 30, 6.0, expect_enforcement=True)  # 6.0% exceeds 5% limit
    
    # 3. PUT OPTIONS - Technical levels within buffer limits (shouldn't enforce)
    await test_technical_stop_flow('AAPL', 200.0, 'put', 1, 0.8, expect_enforcement=False)  # 0.8% within 1% limit
    await test_technical_stop_flow('MSFT', 400.0, 'put', 2, 1.9, expect_enforcement=False)  # 1.9% within 2% limit
    await test_technical_stop_flow('TSLA', 250.0, 'put', 5, 2.8, expect_enforcement=False)  # 2.8% within 3% limit
    await test_technical_stop_flow('GOOG', 180.0, 'put', 30, 4.2, expect_enforcement=False)  # 4.2% within 5% limit
    await test_technical_stop_flow('GOOG', 180.0, 'put', 90, 6.5, expect_enforcement=False)  # 6.5% within 7% limit
    
    # 4. PUT OPTIONS - Technical levels exceeding buffer limits (should enforce)
    await test_technical_stop_flow('AAPL', 200.0, 'put', 1, 1.2, expect_enforcement=True)  # 1.2% exceeds 1% limit
    await test_technical_stop_flow('MSFT', 400.0, 'put', 2, 2.3, expect_enforcement=True)  # 2.3% exceeds 2% limit
    await test_technical_stop_flow('TSLA', 250.0, 'put', 5, 3.6, expect_enforcement=True)  # 3.6% exceeds 3% limit
    await test_technical_stop_flow('GOOG', 180.0, 'put', 30, 5.5, expect_enforcement=True)  # 5.5% exceeds 5% limit
    await test_technical_stop_flow('GOOG', 180.0, 'put', 90, 7.5, expect_enforcement=True)  # 7.5% exceeds 7% limit

if __name__ == "__main__":
    print("===== VERIFYING BUFFER ENFORCEMENT WITH END-TO-END TESTING =====")
    print("This test will verify the entire flow from technical analysis to display")
    print("Buffer enforcement should ONLY happen when technical level exceeds limits")
    
    # Run the async tests
    import asyncio
    asyncio.run(run_tests())
    
    print("\n===== TESTING COMPLETE =====")