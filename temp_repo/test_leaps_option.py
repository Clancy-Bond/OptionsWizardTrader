"""
Test script to check the long-term option (LEAPS) format for stop loss recommendations
with proper weekly theta decay intervals
"""
import traceback
import sys
import asyncio
from discord_bot import OptionsBot

async def test_leaps_option():
    """Test the long-term (LEAPS) stop loss recommendation"""
    print("\n===== TESTING LEAPS OPTION STOP LOSS RECOMMENDATION WITH WEEKLY DECAY INTERVALS =====")
    
    try:
        # Initialize the bot
        bot = OptionsBot()
        
        # Create a mock message with a long-term LEAPS option request
        class MockMessage:
            content = "What's a good stop loss for my AAPL 220 calls expiring January 16th 2026?"
            
            async def reply(self, content=None, embed=None):
                print("\n===== BOT RESPONSE (LEAPS OPTION) =====\n")
                
                # If the response is an embed, print its fields
                if embed:
                    # Access the description and fields
                    if hasattr(embed, "description"):
                        print("DESCRIPTION:")
                        print(embed.description)
                    
                    # Print each field
                    if hasattr(embed, 'fields'):
                        print("\nFIELDS:")
                        for idx, field in enumerate(embed.fields):
                            print(f"\nField {idx+1} - Name: {field.name}")
                            print(f"Field {idx+1} - Value: {field.value}")
                    
                    return embed
                    
                # If it's just content, print that
                print(content)
                return content
                
        class MockUser:
            def __init__(self):
                self.id = "12345"
                self.name = "Test User"
                self.bot = False
                
        # Set up the mock message with author
        mock_message = MockMessage()
        mock_message.author = MockUser()
        
        # Process the mock message
        response = await bot.handle_message(mock_message)
        
        # Print response details
        print("\n===== DIRECT RESPONSE OBJECT =====")
        print(f"Response type: {type(response)}")
        if hasattr(response, 'description'):
            print("\nDescription:")
            print(response.description)
        
        if hasattr(response, 'fields'):
            print("\nFields:")
            for i, field in enumerate(response.fields):
                print(f"\nField {i}:")
                print(f"Name: {field.name}")
                # Print full field value for debugging
                print(f"Value (First 150 chars): {field.value[:150]}" + ("..." if len(field.value) > 150 else ""))
                print(f"Inline: {field.inline}")
                
            # Print all field names for easier inspection
            print("\nAll field names:")
            all_names = [field.name for field in response.fields]
            print(all_names)
        
        # Check the response
        passes = 0
        tests = 0
        
        if response:
            # Check for weekly theta decay intervals
            tests += 1
            weekly_intervals = "**Week 1" in response.description and "**Week 2" in response.description
            if weekly_intervals:
                print("\n✅ PASS: Weekly theta decay intervals are correctly shown for LEAPS option!")
                passes += 1
            else:
                print("\n❌ ERROR: Weekly theta decay intervals are not displayed correctly for LEAPS option!")
                
            # Check for long-term trade recommendation (field names might vary)
            tests += 1
            long_term_found = False
            field_names = []
            field_values = []
            
            for field in response.fields:
                field_names.append(field.name)
                field_values.append(field.value[:100] if field.value else "")
                if "LONG-TERM" in field.name.upper() or "LEAPS" in field.name.upper():
                    long_term_found = True
            
            if long_term_found:
                print("✅ PASS: Long-term trade recommendation shown correctly!")
                passes += 1
            else:
                print("❌ ERROR: Long-term trade recommendation not found!")
                
            # Check for duplicate fields with same content (indicating Analysis field duplication)
            tests += 1
            has_duplicates = False
            duplicate_field_names = []
            
            # Create a detailed analysis of all fields and their contents for debugging
            print("\n=== DETAILED FIELD ANALYSIS ===")
            for i, field in enumerate(response.fields):
                print(f"Field {i}: '{field.name}'")
                print(f"  Content starts with: '{field.value[:50]}'...")
                print(f"  Contains 'LONG-TERM': {('LONG-TERM' in field.value.upper())}")
                print(f"  Contains 'LONG-TERM TRADE': {('LONG-TERM TRADE' in field.value.upper())}")
                print(f"  Contains 'LONG-TERM STOP LOSS': {('LONG-TERM STOP LOSS' in field.value.upper())}")
                print(f"  Field name is Analysis: {field.name == '⭐ Analysis ⭐'}")
                
            # Check if Analysis field contains LONG-TERM in its content
            for i, field in enumerate(response.fields):
                if (field.name == "⭐ Analysis ⭐" and 
                    ("LONG-TERM" in field.value.upper() or "LONG-TERM TRADE" in field.value.upper() or
                     "LONG-TERM STOP LOSS" in field.value.upper())):
                    has_duplicates = True
                    duplicate_field_names.append(field.name)
                    print(f"WARNING: Found duplicate content in field '{field.name}':")
                    print(f"  Content: '{field.value[:100]}...'")
                    
            # Check for any field with "Analysis" in the name for broader detection
            for i, field in enumerate(response.fields):
                if ("ANALYSIS" in field.name.upper() and 
                    ("LONG-TERM" in field.value.upper() or "LONG-TERM TRADE" in field.value.upper())):
                    has_duplicates = True
                    duplicate_field_names.append(field.name)
                    print(f"WARNING: Found duplicate content in field with 'Analysis' in name: '{field.name}':")
                    print(f"  Content: '{field.value[:100]}...'")
            print("=== END FIELD ANALYSIS ===")
            
            if not has_duplicates:
                print("✅ PASS: No duplicate Long-term content in Analysis field!")
                passes += 1
            else:
                print(f"❌ ERROR: Found duplicate Long-term content in fields: {duplicate_field_names}")
                print("  This means the Analysis field is showing the same info as the LONG-TERM STOP LOSS field.")
                
            # Print summary - make sure it's visible
            print("\n################################################")
            print(f"TEST SUMMARY: {passes}/{tests} tests passing ({passes/tests*100:.0f}%)")
            
            if passes == tests:
                print("✅✅✅ ALL TESTS PASSED! The duplicate LONG-TERM STOP LOSS issue has been fixed! ✅✅✅")
            else:
                print("❌❌❌ SOME TESTS FAILED! Please check the details above. ❌❌❌")
            print("################################################")
        else:
            print("No response received from the bot!")
            
    except Exception as e:
        print(f"\n❌❌❌ ERROR IN TEST: {str(e)} ❌❌❌")
        print(traceback.format_exc())
        print("\nAttempting to debug response object directly:")
        try:
            print(f"Response type: {type(response)}")
            print(f"Response dir: {dir(response)}")
            if hasattr(response, 'to_dict'):
                print(f"Response dict: {response.to_dict()}")
            else:
                print("Response does not have to_dict method")
        except Exception as debug_e:
            print(f"Debug error: {debug_e}")
        
    print("\n===== END OF TEST =====")

if __name__ == "__main__":
    asyncio.run(test_leaps_option())