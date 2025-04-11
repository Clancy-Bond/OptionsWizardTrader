"""
This is an improved test script that checks our latest updates to the bot format
"""
import asyncio
import datetime

from discord_bot import OptionsBot

def test_stop_loss_recommendation():
    """Test the stop loss recommendation functionality with the updated format"""
    try:
        print("\n===== TESTING IMPROVED STOP LOSS RECOMMENDATION FORMAT =====")
        
        # Create a bot instance
        bot = OptionsBot()
        
        # Create a mock message
        class MockMessage:
            content = "What's a good stop loss for my TSLA 270 calls expiring April 4?"
            
        mock_message = MockMessage()
        
        # Initialize with test values for TSLA
        test_info = {
            'ticker': 'TSLA',
            'strike': 270.0,
            'option_type': 'call',
            'expiration': '2025-04-04',
            'contract_count': 2
        }
        
        # Call the stop loss function
        response = asyncio.run(bot.handle_stop_loss_request(
            message=mock_message,
            info=test_info
        ))
        
        # Check if we got a real response from the bot
        if response is None:
            print("ERROR: The bot returned None - check your return statements!")
        else:
            # We got a real response from the bot
            print("Bot returned a valid response!")
            
            # Print the description content
            if hasattr(response, 'description'):
                print("\n===== DESCRIPTION CONTENT =====")
                print(response.description)
                
                # Check specifically for the presence of our updated text format
                if "**What happens to your option at the stop level?**" in response.description:
                    print("\n❌ ERROR: Old stop level heading is still present in the response!")
                else:
                    print("\n✅ PASS: Old stop level heading has been successfully removed!")
                
                # Check if any field contains the new format text
                format_found = False
                if hasattr(response, 'fields'):
                    for field in response.fields:
                        if isinstance(field, dict):
                            if "Options typically lose" in str(field.get('value', '')):
                                format_found = True
                                break
                        else:
                            if "Options typically lose" in str(field):
                                format_found = True
                                break
                                
                if format_found:
                    print("✅ PASS: New format 'Options typically lose' is present in the response!")
                else:
                    print("❌ ERROR: New format text is missing! Text should include 'Options typically lose'")
                
                # Check for theta decay position (it should appear in the description)
                if "THETA DECAY PROJECTION" in response.description:
                    print("✅ PASS: Theta decay appears in the description as required!")
                else:
                    print("❌ ERROR: Theta decay projection not found in description!")
                    
                # Print each field for additional verification
                if hasattr(response, 'fields'):
                    print("\n===== FIELDS CONTENT =====")
                    for field in response.fields:
                        if isinstance(field, dict):
                            print(f"\n{field.get('name', '')}")
                            print(f"{field.get('value', '')}")
                        else:
                            print(f"\nField: {field}")
                        
            else:
                print(f"Unknown response format: {type(response)}")
                
        print("===== END OF TEST =====")
        
    except Exception as e:
        import traceback
        print(f"Error in test: {str(e)}")
        print(traceback.format_exc())

if __name__ == "__main__":
    test_stop_loss_recommendation()