"""
Test script for the options bot responses
"""
import json
import asyncio
import os
import datetime

from discord_bot import OptionsBot

def test_option_price_prediction(num_contracts=1):
    """Simulate a response with multiple contracts"""
    
    # Sample data
    ticker = "AAPL"
    strike_price = 230.0
    option_type = "call"
    current_price = 217.90
    option_price = 3.56
    target_price = 245.0
    target_date = datetime.datetime.now() + datetime.timedelta(days=7)
    target_days = 7
    date_adjusted_price = 10.38
    profit_amount = (date_adjusted_price - option_price) * 100
    profit_sign = "+" if profit_amount > 0 else ""
    
    # Test with different contract counts
    for contract_count in [1, 5, 15]:
        # Calculate total profit based on contract count
        total_profit = profit_amount * contract_count
        total_profit_sign = "+" if total_profit > 0 else ""
        
        # Format response with target date
        target_date_display = target_date.strftime("%A, %B %d, %Y")
        
        response = (
            f"📊 **{ticker} ${strike_price} {option_type.upper()} Prediction** 📊\n\n"
            f"• Current Stock Price: ${current_price:.2f}\n"
            f"• Current Option Price: ${option_price:.2f}\n\n"
            f"• By {target_date_display} (in {target_days} days):\n"
            f"• If {ticker} reaches ${target_price:.2f}:\n"
            f"• Estimated Option Price: ${date_adjusted_price:.2f}\n"
            f"• Profit/Loss: {profit_sign}${profit_amount:.2f} per contract\n"
        )
        
        # Add total profit/loss if more than 1 contract
        if contract_count > 1:
            response += f"• Total for {contract_count} contracts: {total_profit_sign}${total_profit:.2f}\n\n"
        else:
            response += "\n"
            
        response += f"*This estimate includes both price movement and time decay effects.*"
        
        print(f"\n===== TEST WITH {contract_count} CONTRACT(S) =====")
        print(response)
        print("========================================")

def test_stop_loss_recommendation():
    """Test the stop loss recommendation functionality"""
    try:
        print("\n===== TESTING STOP LOSS RECOMMENDATION =====")
        # Create a bot instance
        bot = OptionsBot()
        
        # Create a mock message
        class MockMessage:
            content = "What's a good stop loss for my AAPL 230 calls expiring April 11?"
            
        mock_message = MockMessage()
        
        # Initialize with default test values
        test_info = {
            'ticker': 'AAPL',
            'strike': 230.0,
            'option_type': 'call',
            'expiration': '2025-04-11',
            # Add additional info that might be needed in fallback cases
            'current_price': 217.90,
            'current_option_price': 3.56
        }
        
        # Call the stop loss function
        try:
            response = asyncio.run(bot.handle_stop_loss_request(
                message=mock_message,
                info=test_info
            ))
            
            # Print the response details
            if hasattr(response, 'description') and response.description:
                print(f"Stop loss recommendation generated successfully! (length: {len(response.description)} chars)")
                print("First 500 characters of response:")
                print(response.description[:500] + "..." if len(response.description) > 500 else response.description)
            else:
                print("No description found in response!")
                print(f"Response type: {type(response)}")
        except Exception as inner_e:
            print(f"Error in handle_stop_loss_request: {str(inner_e)}")
            import traceback
            print(traceback.format_exc())
    
        print("========================================")
    except Exception as e:
        print(f"Error testing stop loss: {str(e)}")
        import traceback
        print(traceback.format_exc())

def main():
    """Main test function that runs both option price tests and stop loss tests"""
    # Run the option price prediction test
    test_option_price_prediction()
    
    # Run the stop loss recommendation test
    test_stop_loss_recommendation()

if __name__ == "__main__":
    main()