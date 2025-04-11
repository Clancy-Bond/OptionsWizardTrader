# Nested Stop Loss Data Structure Fix

## Problem Identified

The Discord bot was encountering None values in `stop_loss_data.get("level")` due to two issues:

1. Different response structures from `get_stop_loss_recommendations()` - sometimes it returns a flat dictionary with a "level" key, and sometimes a nested structure with "swing" or "primary" dictionaries containing the "level" key.

2. The existing code was not handling these variations, causing a ValueError when trying to format None values in f-strings.

## Solution Implemented

We've enhanced the `handle_stop_loss_request` method to:

1. Extract the stop level from multiple possible data structures:
   - Direct `"level"` key in the top-level dictionary
   - Nested inside `"swing"` dictionary
   - Nested inside `"primary"` dictionary

2. Implemented safer logging with appropriate None value handling.

3. Added fallback mechanics to properly use `technical_stop` when a level can't be found in the response data.

## Test Results

We created a test script (`test_nested_stop_loss_data.py`) that verifies our solution works with all the different data structures:

1. Direct level dictionary: ✅ Successfully extracts level
2. Nested "swing" structure: ✅ Successfully extracts level
3. Nested "primary" structure: ✅ Successfully extracts level
4. Combined nested structure: ✅ Successfully extracts level (prioritizes "swing")
5. Missing level key: ✅ Properly handles with fallback, avoiding errors

## Benefits

This fix ensures:
- No runtime errors due to None values in string formatting
- More resilient handling of different response structures
- Clear logging to help debugging
- Consistent user experience with proper fallbacks

## Next Steps

Monitor the Discord bot logs to ensure there are no more issues with:
1. None values in stop loss calculations
2. Handling of nested data structures
3. Appropriate display of technical stop levels vs. buffer-adjusted levels

The code is now more robust and better prepared to handle varying response formats from the technical analysis module.