"""
Test script to verify the stop loss buffer percentage is correctly displayed for PUT options
in the Discord bot.

This script simulates a stop loss request and checks that the buffer percentage 
is displayed as expected based on days to expiration.
"""

import asyncio
import discord
from datetime import datetime, timedelta
import sys
from discord_bot import OptionsBot

class TestPutBufferFix:
    """Test class to verify the correct display of PUT option buffer percentages."""
    
    def __init__(self):
        """Initialize the test class."""
        self.bot = OptionsBot()
    
    async def run_test(self):
        """Run test cases with different expiration dates to verify buffer percentages."""
        print("Testing PUT option buffer percentage display:")
        print("-" * 50)
        
        # Test cases with SPY's actual available expiration dates
        test_cases = [
            {"ticker": "SPY", "price": 499.50, "option_type": "put", "strike": 500, "expiration": "2025-04-08", "expected_buffer": 1.0},
            {"ticker": "SPY", "price": 499.50, "option_type": "put", "strike": 500, "expiration": "2025-04-09", "expected_buffer": 2.0},
            {"ticker": "SPY", "price": 499.50, "option_type": "put", "strike": 500, "expiration": "2025-04-11", "expected_buffer": 3.0},
            {"ticker": "SPY", "price": 499.50, "option_type": "put", "strike": 500, "expiration": "2025-04-25", "expected_buffer": 5.0},
            {"ticker": "SPY", "price": 499.50, "option_type": "put", "strike": 500, "expiration": "2025-07-18", "expected_buffer": 7.0},
        ]
        
        # Also test the same with calls to make sure we didn't break anything
        call_test_cases = [
            {"ticker": "SPY", "price": 500.50, "option_type": "call", "strike": 500, "expiration": "2025-04-08", "expected_buffer": 1.0},
            {"ticker": "SPY", "price": 500.50, "option_type": "call", "strike": 500, "expiration": "2025-04-11", "expected_buffer": 3.0},
        ]
        
        # Combine test cases
        all_test_cases = test_cases + call_test_cases
        
        for test_case in all_test_cases:
            await self.test_buffer_display(**test_case)
            
        print("\nAll tests completed!")
    
    async def test_buffer_display(self, ticker, price, option_type, strike, expiration, expected_buffer):
        """Test a specific buffer display scenario."""
        # Setup mock message and info
        class MockMessage:
            async def reply(self, content=None, embed=None):
                # Check the embed for correct buffer percentage
                if embed:
                    # Print all embed fields for debugging
                    print(f"\nDEBUG - Embed for {option_type.upper()} with expiration {expiration}:")
                    print(f"Title: {embed.title}")
                    print(f"Description: {embed.description}")
                    print(f"Number of fields: {len(embed.fields)}")
                    
                    for i, field in enumerate(embed.fields):
                        print(f"Field {i+1} - Name: '{field.name}', Value: '{field.value[:50]}...'")
                    
                    # Extract the buffer percentage from the embed field value
                    found = False
                    for field in embed.fields:
                        if "Stock Price Stop Level:" in field.value:
                            found = True
                            # Extract the percentage
                            start_idx = field.value.find("(") + 1
                            end_idx = field.value.find("%")
                            if start_idx > 0 and end_idx > 0:
                                actual_buffer = float(field.value[start_idx:end_idx])
                                result = "✅ PASS" if abs(actual_buffer - expected_buffer) < 0.1 else "❌ FAIL"
                                print(f"{result} - {option_type.upper()} with expiration {expiration}: Expected {expected_buffer}%, got {actual_buffer}%")
                                # Print the full embed field for debugging
                                print(f"Full field value: {field.value}")
                                return
                    
                    if not found:
                        print(f"❌ FAIL - Could not find 'Stock Price Stop Level:' in any field for {option_type.upper()} with expiration {expiration}")
                
                print(f"❌ FAIL - Could not find buffer percentage in embed for {option_type.upper()} with expiration {expiration}")
        
        # Setup information dictionary
        info = {
            "ticker": ticker,
            "strike_price": strike,
            "option_type": option_type,
            "expiration_date": expiration,
            "request_type": "stop_loss",
        }
        
        # Create a mock message
        message = MockMessage()
        
        # Call the handler method with controlled parameters
        try:
            await self.bot.handle_stop_loss_request(message, info)
        except Exception as e:
            print(f"Error during test: {e}")

async def main():
    """Main function to run tests."""
    tester = TestPutBufferFix()
    await tester.run_test()

if __name__ == "__main__":
    asyncio.run(main())