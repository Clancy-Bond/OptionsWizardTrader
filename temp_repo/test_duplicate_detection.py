"""
Comprehensive test script to verify the fix for duplicate stop loss field issues.
This script specifically tests different types of stop loss recommendations and
ensures that there are no duplicated fields in the Discord bot's responses.
"""

import os
import sys
import asyncio
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler()])

logger = logging.getLogger("DuplicateDetectionTest")

# Import the discord bot
try:
    from discord_bot import OptionsBot, OptionsBotNLP
    logger.info("Successfully imported Discord bot modules")
except Exception as e:
    logger.error(f"Failed to import Discord bot modules: {str(e)}")
    sys.exit(1)

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
        logger.info(f"Reply sent with embed: {embed is not None}")
        if embed:
            # Add a fields attribute to our embed for inspection if it doesn't exist
            if not hasattr(embed, 'fields'):
                embed.fields = []
            logger.info(f"Embed has {len(embed.fields)} fields")
            return embed
        return content

async def test_long_term_stop_loss():
    """Test a long-term LEAP stop loss recommendation and check for duplicate fields"""
    logger.info("===== TESTING LONG TERM STOP LOSS =====")
    
    # Create message with a long-term stop loss query
    message = MockMessage("What's a good stop loss for my AAPL 220 calls expiring January 16th 2026?")
    
    # Create bot instance
    bot = OptionsBot()
    
    # Process message
    logger.info("Processing long-term stop loss message...")
    response = await bot.handle_message(message)
    
    # Check for response
    if response:
        logger.info("✅ Got response from bot")
        
        # Check for fields (we should have fields for a proper embed response)
        if hasattr(response, 'fields'):
            logger.info(f"Response has {len(response.fields)} fields")
            
            # Print all field names for debugging
            field_names = [field.name for field in response.fields]
            logger.info(f"Field names: {field_names}")
            
            # Check for duplicate fields by name
            if len(field_names) != len(set(field_names)):
                logger.error("❌ Found duplicate field names!")
                duplicates = [name for name in field_names if field_names.count(name) > 1]
                logger.error(f"Duplicate field names: {duplicates}")
                return False
            
            # Check if 'LONG-TERM STOP LOSS' appears in multiple field values
            long_term_content_count = 0
            for field in response.fields:
                if "LONG-TERM STOP LOSS" in field.value.upper():
                    long_term_content_count += 1
                    logger.info(f"Field with LONG-TERM STOP LOSS content: {field.name}")
                
            if long_term_content_count > 1:
                logger.error(f"❌ Found LONG-TERM STOP LOSS content in {long_term_content_count} fields (should be 1)")
                return False
                
            # Check if Analysis field contains LONG-TERM in its content
            has_duplicate_content = False
            for field in response.fields:
                if (field.name == "⭐ Analysis ⭐" and 
                    ("LONG-TERM STOP LOSS" in field.value.upper() or
                     "LONG-TERM TRADE STOP LOSS" in field.value.upper())):
                    logger.error("❌ Analysis field contains LONG-TERM STOP LOSS content - this is a duplicate!")
                    logger.error(f"Analysis field content starts with: {field.value[:50]}...")
                    has_duplicate_content = True
                    return False
            
            if not has_duplicate_content:
                logger.info("✅ No duplicate content detected between Analysis and LONG-TERM STOP LOSS fields")
                return True
        else:
            logger.error("❌ Response doesn't have fields")
            return False
    else:
        logger.error("❌ No response received from bot")
        return False

async def test_swing_trade_stop_loss():
    """Test a swing trade stop loss recommendation and check for duplicate fields"""
    logger.info("===== TESTING SWING TRADE STOP LOSS =====")
    
    # Create message with a swing trade stop loss query
    message = MockMessage("What's a good stop loss for my TSLA 270 calls expiring Apr 25th 2025?")
    
    # Create bot instance
    bot = OptionsBot()
    
    # Process message
    logger.info("Processing swing trade stop loss message...")
    response = await bot.handle_message(message)
    
    # Check for response
    if response:
        logger.info("✅ Got response from bot")
        
        # Check for fields (we should have fields for a proper embed response)
        if hasattr(response, 'fields'):
            logger.info(f"Response has {len(response.fields)} fields")
            
            # Print all field names for debugging
            field_names = [field.name for field in response.fields]
            logger.info(f"Field names: {field_names}")
            
            # Check for duplicate fields by name
            if len(field_names) != len(set(field_names)):
                logger.error("❌ Found duplicate field names!")
                duplicates = [name for name in field_names if field_names.count(name) > 1]
                logger.error(f"Duplicate field names: {duplicates}")
                return False
            
            # Check if 'SWING TRADE STOP LOSS' appears in multiple field values
            swing_content_count = 0
            for field in response.fields:
                if "SWING TRADE STOP LOSS" in field.value.upper():
                    swing_content_count += 1
                    logger.info(f"Field with SWING TRADE STOP LOSS content: {field.name}")
                
            if swing_content_count > 1:
                logger.error(f"❌ Found SWING TRADE STOP LOSS content in {swing_content_count} fields (should be 1)")
                return False
                
            # Check if Analysis field contains SWING content
            has_duplicate_content = False
            for field in response.fields:
                if (field.name == "⭐ Analysis ⭐" and 
                    "SWING TRADE STOP LOSS" in field.value.upper()):
                    logger.error("❌ Analysis field contains SWING TRADE STOP LOSS content - this is a duplicate!")
                    logger.error(f"Analysis field content starts with: {field.value[:50]}...")
                    has_duplicate_content = True
                    return False
            
            if not has_duplicate_content:
                logger.info("✅ No duplicate content detected between Analysis and SWING TRADE STOP LOSS fields")
                return True
        else:
            logger.error("❌ Response doesn't have fields")
            return False
    else:
        logger.error("❌ No response received from bot")
        return False

async def test_scalp_trade_stop_loss():
    """Test a scalp trade stop loss recommendation and check for duplicate fields"""
    logger.info("===== TESTING SCALP TRADE STOP LOSS =====")
    
    # Create message with a scalp trade stop loss query
    message = MockMessage("What's a good stop loss for my AMD 170 calls expiring tomorrow?")
    
    # Create bot instance
    bot = OptionsBot()
    
    # Process message
    logger.info("Processing scalp trade stop loss message...")
    response = await bot.handle_message(message)
    
    # Check for response
    if response:
        logger.info("✅ Got response from bot")
        
        # Check for fields (we should have fields for a proper embed response)
        if hasattr(response, 'fields'):
            logger.info(f"Response has {len(response.fields)} fields")
            
            # Print all field names for debugging
            field_names = [field.name for field in response.fields]
            logger.info(f"Field names: {field_names}")
            
            # Check for duplicate fields by name
            if len(field_names) != len(set(field_names)):
                logger.error("❌ Found duplicate field names!")
                duplicates = [name for name in field_names if field_names.count(name) > 1]
                logger.error(f"Duplicate field names: {duplicates}")
                return False
            
            # Check if 'SCALP TRADE STOP LOSS' appears in multiple field values
            scalp_content_count = 0
            for field in response.fields:
                if "SCALP TRADE STOP LOSS" in field.value.upper():
                    scalp_content_count += 1
                    logger.info(f"Field with SCALP TRADE STOP LOSS content: {field.name}")
                
            if scalp_content_count > 1:
                logger.error(f"❌ Found SCALP TRADE STOP LOSS content in {scalp_content_count} fields (should be 1)")
                return False
                
            # Check if Analysis field contains SCALP content
            has_duplicate_content = False
            for field in response.fields:
                if (field.name == "⭐ Analysis ⭐" and 
                    "SCALP TRADE STOP LOSS" in field.value.upper()):
                    logger.error("❌ Analysis field contains SCALP TRADE STOP LOSS content - this is a duplicate!")
                    logger.error(f"Analysis field content starts with: {field.value[:50]}...")
                    has_duplicate_content = True
                    return False
            
            if not has_duplicate_content:
                logger.info("✅ No duplicate content detected between Analysis and SCALP TRADE STOP LOSS fields")
                return True
        else:
            logger.error("❌ Response doesn't have fields")
            return False
    else:
        logger.error("❌ No response received from bot")
        return False

async def run_all_tests():
    """Run all tests and report results"""
    tests_passed = 0
    total_tests = 3
    
    # Run all tests
    long_term_result = await test_long_term_stop_loss()
    if long_term_result:
        tests_passed += 1
    
    swing_result = await test_swing_trade_stop_loss()
    if swing_result:
        tests_passed += 1
    
    scalp_result = await test_scalp_trade_stop_loss()
    if scalp_result:
        tests_passed += 1
    
    # Report results
    logger.info("===== TEST RESULTS =====")
    logger.info(f"Tests passed: {tests_passed}/{total_tests}")
    logger.info(f"Long-term stop loss test: {'PASS' if long_term_result else 'FAIL'}")
    logger.info(f"Swing trade stop loss test: {'PASS' if swing_result else 'FAIL'}")
    logger.info(f"Scalp trade stop loss test: {'PASS' if scalp_result else 'FAIL'}")
    
    if tests_passed == total_tests:
        logger.info("✅✅✅ ALL TESTS PASSED! The duplicate field issue has been fixed! ✅✅✅")
    else:
        logger.info("❌❌❌ SOME TESTS FAILED! Please check the details above. ❌❌❌")

if __name__ == "__main__":
    logger.info("Starting duplicate detection tests...")
    asyncio.run(run_all_tests())