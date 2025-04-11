# Stop Loss Buffer Fix Test Instructions

## Problem Fixed

We've fixed critical issues with how the Discord bot handles stop loss calculations and displays technical levels vs. buffer-enforced levels.

## Test Scenarios to Verify

1. **CALL Option with Technical Level Within Buffer Limits**
   ```
   @SWJ Options AI-Calculator stop loss recommendation for my TSLA Calls with a strike price of 290 and an expiration of 2025-05-02
   ```
   Expected result: Should show the actual technical level (around $217)

2. **CALL Option with Technical Level Exceeding Buffer Limits**
   ```
   @SWJ Options AI-Calculator stop loss recommendation for my TSLA Calls with a strike price of 290 and an expiration of 2025-05-16
   ```
   Expected result: Should show buffer-enforced level

3. **PUT Option with Technical Level Within Buffer Limits**
   ```
   @SWJ Options AI-Calculator stop loss recommendation for my TSLA Puts with a strike price of 190 and an expiration of 2025-05-02
   ```
   Expected result: Should show the actual technical level

4. **PUT Option with Technical Level Exceeding Buffer Limits**
   ```
   @SWJ Options AI-Calculator stop loss recommendation for my TSLA Puts with a strike price of 190 and an expiration of 2025-05-16
   ```
   Expected result: Should show buffer-enforced level

## What to Look For

1. Check if the "Stock Price Stop Level" matches the technical level in logs when enforcement is not needed.
2. Verify that detailed logs show "Buffer was enforced: False" when the technical level is within limits.
3. Confirm correct buffer percentages are displayed based on days to expiration.

## New Safeguards

1. Added proper conversions between numpy.float64 and Python floats
2. Added fallback for None values in any part of the calculation
3. Added detailed debugging output at every step
4. Fixed log messages to clearly distinguish between technical levels and buffer limits