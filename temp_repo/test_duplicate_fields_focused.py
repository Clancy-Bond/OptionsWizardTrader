"""
Focused test script to verify the fix for duplicate stop loss field issues.
This script specifically tests the TSLA stop loss case that previously had issues.
"""

import asyncio
import traceback

class MockUser:
    def __init__(self):
        self.id = 123456789
        self.name = "TestUser"
        self.display_name = "Test User"

class MockMessage:
    def __init__(self, content):
        self.content = content
        self.author = MockUser()
        self._sent_reply = None
        self._sent_embed = None
        
    async def reply(self, content=None, embed=None):
        self._sent_reply = content
        self._sent_embed = embed
        print(f"Reply sent with embed: {embed is not None}")
        return embed or content

async def test_tsla_stop_loss():
    """
    Test the specific TSLA stop loss case that was having issues
    This was the query that showed duplicated LONG-TERM STOP LOSS fields
    """
    print("\n===== TESTING TSLA STOP LOSS (Previously problematic case) =====")
    
    # The original TSLA query that was causing issues
    message = MockMessage("What's a good stop loss for my TSLA $270 calls expiring Apr 4th 2025?")
    
    try:
        # Import the bot (do this in function to avoid global import errors)
        from discord_bot import OptionsBot
        
        # Create bot instance
        bot = OptionsBot()
        
        # Process message
        print("Processing TSLA stop loss message...")
        response = await bot.handle_message(message)
        
        # Check for response
        if response:
            print("✅ Got response from bot")
            
            # Check if the response has fields (should be an embed)
            if hasattr(response, 'fields'):
                # Check for fields (we should have fields for a proper embed response)
                field_count = len(response.fields)
                print(f"Response has {field_count} fields")
                
                # Print all field names for debugging
                print("\nField names:")
                for i, field in enumerate(response.fields):
                    print(f"  {i+1}. {field.name}")
                
                # Print a portion of each field's content for inspection
                print("\nField contents (truncated):")
                for i, field in enumerate(response.fields):
                    print(f"  {i+1}. {field.name}: {field.value[:50]}...")
                
                # Check for duplicate fields by name
                field_names = [field.name for field in response.fields]
                if len(field_names) != len(set(field_names)):
                    print("❌ ERROR: Found duplicate field names!")
                    duplicates = [name for name in field_names if field_names.count(name) > 1]
                    print(f"Duplicate field names: {duplicates}")
                    return False
                
                # Search for fields containing long-term stop loss content
                long_term_fields = []
                for i, field in enumerate(response.fields):
                    if "LONG-TERM STOP LOSS" in field.value.upper():
                        long_term_fields.append(i)
                
                if len(long_term_fields) > 1:
                    print(f"❌ ERROR: Found LONG-TERM STOP LOSS content in {len(long_term_fields)} fields")
                    for idx in long_term_fields:
                        print(f"  Field {idx+1}: {response.fields[idx].name}")
                    return False
                elif len(long_term_fields) == 1:
                    print(f"✅ LONG-TERM STOP LOSS appears in exactly one field: {response.fields[long_term_fields[0]].name}")
                else:
                    print("Note: No LONG-TERM STOP LOSS fields found (this might be a swing trade recommendation)")
                
                # Search for Analysis field with duplicate content
                for field in response.fields:
                    if (field.name == "⭐ Analysis ⭐" and 
                        ("LONG-TERM STOP LOSS" in field.value.upper() or 
                         "SWING TRADE STOP LOSS" in field.value.upper() or
                         "SCALP TRADE STOP LOSS" in field.value.upper())):
                        print(f"❌ ERROR: Analysis field contains stop loss content - this is a duplicate!")
                        print(f"Content starts with: {field.value[:50]}...")
                        return False
                
                print("\n✅ PASS: No duplicate fields or content detected")
                print("The issue has been fixed! 🎉")
                return True
            else:
                print("❌ ERROR: Response doesn't have fields attribute")
                return False
        else:
            print("❌ ERROR: No response received from bot")
            return False
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("Starting TSLA stop loss duplicate detection test...")
    result = asyncio.run(test_tsla_stop_loss())
    
    print("\n===== TEST RESULT =====")
    if result:
        print("✅✅✅ TEST PASSED! The duplicate field issue has been fixed! ✅✅✅")
    else:
        print("❌❌❌ TEST FAILED! Please check the details above. ❌❌❌")