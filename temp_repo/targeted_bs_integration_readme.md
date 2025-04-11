# Targeted Black-Scholes Integration for Edge Cases

## Overview

This project implements a targeted enhancement to the option price calculator in our Discord bot by using full Black-Scholes recalculation **only** for specific problematic cases - namely, at-the-money (ATM) options near expiration where the standard delta approximation produces unrealistic results.

## Problem Statement

When calculating the potential loss at stop loss levels for near-expiration ATM options, our bot sometimes reports unrealistic values like "Option Price at Stop: $8.83 (0.0% loss)" even when the stop price is significantly different from the current price. This occurs because:

1. **Delta values near zero**: For ATM options on expiration day, delta values can be extremely small due to mathematical peculiarities in the Black-Scholes model
2. **Division by zero errors**: These can occur in the underlying calculations, resulting in unreliable delta values
3. **Linear approximation failure**: The delta approximation assumes a linear relationship that breaks down severely for ATM options near expiration

As a result, users get misleading information about their potential losses, which could impact their trading decisions.

## Test Results

Our testing revealed that for near-expiration ATM options, the delta approximation can severely underestimate potential losses:

### SPY PUT Test Case (Expiration Day)
- SPY PUT at $496.00 strike
- Current stock price: $496.48
- Current option price: $8.83
- Stop loss level: $501.44 (1.0% buffer)

| Method | Price at Stop | % Change |
|--------|--------------|----------|
| Delta Approximation | $6.85 | -22.5% loss |
| Black-Scholes | $0.03 | -99.6% loss |

## Solution: Targeted Implementation

Rather than completely replacing the delta approximation for all scenarios, we've implemented a targeted approach that:

1. Uses standard delta approximation for most options (computationally efficient)
2. Identifies problematic cases using specific criteria:
   - Option is near expiration (≤ 1 DTE)
   - Option is at or near the money (price within 0.5% of strike)
   - Delta value is unrealistically small (< 0.2)
3. Only for these specific cases, uses full Black-Scholes recalculation
4. Includes fallback to enhanced delta approximation if BS calculation fails

This approach combines accuracy in edge cases with computational efficiency for normal cases.

## Implementation Details

The enhanced calculation is implemented with two main components:

1. `option_price_calculator.py`: Module with BS calculation functions
2. `targeted_bs_integration.py`: Script that adds conditional logic to the Discord bot

### Key Components in the Calculator Module

- `black_scholes(S, K, T, r, sigma, option_type)`: Core BS calculation function
- `calculate_option_price_at_stop(...)`: Unified interface supporting both calculation methods

### Integration Approach

The integration script modifies the Discord bot to:

1. Detect problematic cases using specific criteria
2. Use full BS calculation only for those edge cases
3. Continue using efficient delta approximation for all other cases
4. Provide appropriate fallback mechanisms for error handling

## Benefits

This targeted enhancement provides:

1. **More accurate loss estimations** for expiration-day ATM options
2. **Minimal computational overhead** by using the more intensive calculation only when needed
3. **Enhanced user trust** without sacrificing performance

## Testing

The test suite in `test_option_price_calculator.py` validates both calculation methods across various scenarios, with particular attention to edge cases.

## Usage Guidelines

This enhancement is specifically designed to address the issue where the bot shows unrealistically small loss percentages (like 0.0%) for near-expiration ATM options at stop loss levels. It's not intended as a complete replacement for the delta approximation in all scenarios.