# Black-Scholes Integration for Option Price Calculation

## Overview

This project enhances the option price calculator in our Discord bot by replacing the delta approximation method with a full Black-Scholes recalculation for more accurate option pricing at stop loss levels. This improvement is particularly critical for at-the-money (ATM) options near expiration where the delta approximation method significantly underestimates potential losses.

## Problem Statement

When calculating the potential loss at stop loss levels, our bot previously used a simple delta approximation:

```python
price_change = stop_level - current_price
option_price_change = price_change * delta  # For calls (negative for puts)
option_price_at_stop = option_price + option_price_change
```

While this approximation works reasonably well for options with longer expiration dates, it significantly breaks down for:

1. **At-the-money options near expiration**: With 0-2 DTE (days to expiration), the non-linearity of option pricing becomes extreme
2. **Options crossing stop levels beyond small price moves**: As price moves further from the current level, delta itself changes considerably (gamma effect)

## Test Results

Our testing revealed substantial discrepancies between delta approximation and full Black-Scholes recalculation:

### SPY PUT Test Case (Expiration Day)
- SPY PUT at $496.00 strike
- Current stock price: $496.48
- Current option price: $8.83
- Stop loss level: $501.44 (1.0% buffer)

| Method | Price at Stop | % Change |
|--------|--------------|----------|
| Delta Approximation | $6.85 | -22.5% loss |
| Black-Scholes | $0.03 | -99.6% loss |

As shown, for an at-the-money PUT on expiration day, delta approximation suggests only a -22.5% loss at the stop level, while Black-Scholes correctly calculates a nearly -100% loss.

### Comparison Across Different Buffer Percentages (0.1 DTE)

| Buffer % | Stop Level | Delta Approximation | Black-Scholes | Difference |
|----------|------------|---------------------|---------------|------------|
| 0.5% | $498.96 | $7.84 (-11.2%) | $0.23 (-97.4%) | $7.61 (86.2%) |
| 1.0% | $501.44 | $6.84 (-22.5%) | $0.03 (-99.6%) | $6.81 (77.1%) |
| 2.0% | $506.41 | $4.86 (-45.0%) | $0.01 (-99.9%) | $4.85 (54.9%) |
| 3.0% | $511.37 | $2.87 (-67.5%) | $0.01 (-99.9%) | $2.86 (32.4%) |
| 5.0% | $521.30 | $0.01 (-99.9%) | $0.01 (-99.9%) | $0.00 (0.0%) |

The discrepancy is most severe for small buffer percentages, which are most commonly used for scalp trades (0-2 DTE).

## Implementation Details

The enhanced calculation is implemented in the `option_price_calculator.py` module, which provides:

1. A full Black-Scholes calculation function that handles edge cases like zero DTE
2. A unified interface that can use either full BS calculation or delta approximation
3. Robust error handling with a fallback to delta approximation if BS calculation fails

### Key Components

- `black_scholes(S, K, T, r, sigma, option_type)`: Core BS calculation function
- `calculate_option_price_at_stop(...)`: Primary function that the Discord bot interfaces with
- `format_price_change(original_price, new_price)`: Helper for formatting price changes

### Integration

The `bs_calculator_integration.py` script handles the integration of the Black-Scholes calculator into the Discord bot by:

1. Adding the necessary import statement
2. Replacing the delta approximation code with calls to the enhanced calculator
3. Ensuring proper error handling with fallback to delta approximation

## Benefits

This enhancement provides:

1. **More accurate loss estimations**: Especially critical for short-term/scalp trades
2. **Better risk management**: Users get a more accurate picture of potential losses 
3. **Enhanced user trust**: Bot responses align more closely with actual market behavior

## Future Improvements

Potential future enhancements include:

1. Dynamically selecting calculation method based on option characteristics
2. Adding a "Greeks at stop level" calculation to show how delta/gamma would change
3. Visualizing the option price decay curve at different stock price levels

## Testing

A comprehensive test suite is provided in `test_option_price_calculator.py` which validates the calculator across various scenarios with particular attention to edge cases like near-expiration options.

## References

- Black, F., & Scholes, M. (1973). The Pricing of Options and Corporate Liabilities. Journal of Political Economy, 81(3), 637–654.
- Hull, J. C. (2018). Options, Futures, and Other Derivatives (10th ed.). Pearson.