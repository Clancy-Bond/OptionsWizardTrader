# LEAPS Weekly-Based Stop Loss System

## Overview
This enhancement implements a specialized stop loss calculation approach for long-term options (LEAPS), defined as options with 180+ days to expiration. 

For these options, we now use a more appropriate weekly-candle structure with ATR-based buffering, rather than standard percentage-based buffer limits. This approach is more suitable for the longer-term nature of LEAPS options.

## Key Features

1. **Weekly Candle Structure**
   - Uses weekly candles instead of daily/hourly for a macro view
   - More appropriate for long-term options with 6+ months of duration
   - Filters out short-term noise that may trigger premature stop-outs

2. **ATR-Based Buffering**
   - Applies 10% of weekly ATR as buffer
   - Adapts to the specific volatility of each stock
   - Avoids one-size-fits-all percentage buffers

3. **Weekly Candle Close Confirmation**
   - Requires a full weekly candle close beyond the stop level
   - Prevents stop-outs during intra-week volatility
   - Adds discipline to the exit process for long-term positions

4. **Threshold**
   - Only applied to options with 180+ days to expiration
   - Prioritized as the primary recommendation for long-term options
   - Integrated alongside other stop loss approaches for comprehensive recommendations

## Implementation Details

The LEAPS weekly-based stop loss is calculated in `leaps_weekly_stop_loss.py` and integrated into the main stop loss recommendation system in `technical_analysis.py`. The system:

1. Identifies if an option qualifies as a LEAPS (180+ DTE)
2. Retrieves weekly candle data for the underlying stock
3. Calculates weekly ATR (Average True Range) 
4. Sets stop levels at:
   - For calls: Weekly candle low - (10% × Weekly ATR)
   - For puts: Weekly candle high + (10% × Weekly ATR)
5. Recommends exit only when a full weekly candle closes beyond these levels

## Advantages

- **Reduced Noise**: By using weekly time frames and requiring weekly candle close confirmation
- **Volatility-Adaptive**: Buffer adjusts automatically based on the stock's own volatility
- **Mental Model**: Ties to actual market behavior rather than arbitrary percentages
- **Macro Focus**: Ensures LEAPS traders maintain a longer-term perspective
- **Decision Discipline**: Promotes a patient, structured approach to managing long-term positions

## Verification

The implementation has been tested with various stocks and option expiration dates to ensure it correctly:
- Applies only to options with 180+ days to expiration
- Uses weekly candle structure and ATR appropriately
- Is prioritized as the primary recommendation for qualified options
- Integrates smoothly with the existing recommendation system

## Use Example

For a LEAPS call option on a stock with:
- Current price: $100
- Weekly candle low: $97
- Weekly ATR: $5
- 365 days to expiration

The system would calculate:
- ATR buffer: $5 × 10% = $0.50
- Stop level: $97 - $0.50 = $96.50
- Only exit if a weekly candle closes below $96.50