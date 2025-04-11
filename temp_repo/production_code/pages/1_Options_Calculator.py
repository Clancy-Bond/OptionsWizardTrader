import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.graph_objects as go
from theme_selector import display_theme_selector
import sys
import os

# Add parent directory to path so we can import modules from the main directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from option_calculator import estimate_option_price, calculate_black_scholes, get_option_chain
from technical_analysis import calculate_support_levels

# Display theme selector
display_theme_selector()

st.title("Options Price Calculator")

with st.container():
    st.markdown("""
    This calculator helps you estimate the future value of options contracts based on potential stock price movements.
    """)

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Stock & Option Details")
        ticker = st.text_input("Ticker Symbol", value="AAPL").upper()
        
        strike_price = st.number_input("Strike Price ($)", min_value=1.0, value=200.0, step=1.0)
        
        option_type = st.radio("Option Type", options=["call", "put"], index=0)
        
        # Date picker for expiration
        today = datetime.date.today()
        one_month_later = today + datetime.timedelta(days=30)
        expiration_date = st.date_input("Expiration Date", value=one_month_later, min_value=today)
        
        num_contracts = st.number_input("Number of Contracts", min_value=1, value=1, step=1)
        
    with col2:
        st.subheader("Target Price Analysis")
        
        target_price = st.number_input("Target Stock Price ($)", min_value=1.0, value=220.0, step=1.0)
        
        target_date = st.date_input("Target Date (when you expect to reach target price)", 
                                    value=today + datetime.timedelta(days=15),
                                    min_value=today,
                                    max_value=expiration_date)

if st.button("Calculate Option Value", type="primary"):
    with st.spinner("Retrieving market data and calculating..."):
        try:
            # Format the expiration date as expected by our calculator function
            expiration_date_str = expiration_date.strftime("%Y-%m-%d")
            
            # Calculate days until target and expiration
            days_to_target = (target_date - today).days
            days_to_expiration = (expiration_date - today).days
            
            # Get current option price
            current_option_price, current_stock_price, greeks, error_message = estimate_option_price(
                ticker, 
                strike_price, 
                option_type, 
                expiration_date_str
            )
            
            if error_message:
                st.error(error_message)
            else:
                # Calculate estimated future option price
                future_option_price, _, _, _ = estimate_option_price(
                    ticker, 
                    strike_price, 
                    option_type, 
                    expiration_date_str,
                    target_price=target_price,
                    days_to_expiration=days_to_expiration - days_to_target
                )
                
                # Calculate profit/loss
                profit_per_contract = (future_option_price - current_option_price) * 100
                total_profit = profit_per_contract * num_contracts
                
                # Format for display
                profit_sign = "+" if profit_per_contract >= 0 else ""
                
                # Display results in a nice card-like format
                st.subheader("Results")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        label="Current Stock Price", 
                        value=f"${current_stock_price:.2f}"
                    )
                    st.metric(
                        label="Target Stock Price", 
                        value=f"${target_price:.2f}", 
                        delta=f"{target_price - current_stock_price:.2f} ({((target_price / current_stock_price) - 1) * 100:.1f}%)"
                    )
                
                with col2:
                    st.metric(
                        label="Current Option Price", 
                        value=f"${current_option_price:.2f}/contract"
                    )
                    st.metric(
                        label="Estimated Future Price", 
                        value=f"${future_option_price:.2f}/contract", 
                        delta=f"{profit_sign}${profit_per_contract / 100:.2f} ({profit_sign}{(profit_per_contract / (current_option_price * 100)) * 100:.1f}%)"
                    )
                
                with col3:
                    st.metric(
                        label="Total Investment", 
                        value=f"${current_option_price * 100 * num_contracts:.2f}"
                    )
                    st.metric(
                        label="Profit/Loss", 
                        value=f"{profit_sign}${total_profit:.2f}", 
                        delta=f"{profit_sign}{(total_profit / (current_option_price * 100 * num_contracts)) * 100:.1f}%"
                    )
                
                # Display the Greeks
                st.subheader("Option Greeks")
                
                greeks_col1, greeks_col2, greeks_col3, greeks_col4, greeks_col5 = st.columns(5)
                
                with greeks_col1:
                    st.metric("Delta", f"{greeks['delta']:.3f}")
                
                with greeks_col2:
                    st.metric("Gamma", f"{greeks['gamma']:.5f}")
                
                with greeks_col3:
                    st.metric("Theta", f"{greeks['theta']:.5f}")
                
                with greeks_col4:
                    st.metric("Vega", f"{greeks['vega']:.5f}")
                
                with greeks_col5:
                    st.metric("Implied Volatility", f"{greeks['impliedVolatility']:.2%}")
                
                # Calculate the support levels for stop-loss recommendations
                support_levels = calculate_support_levels(ticker)
                
                if support_levels and len(support_levels) > 0:
                    st.subheader("Technical Support Levels")
                    
                    # Create a price chart with support levels
                    fig = go.Figure()
                    
                    # Add support levels as horizontal lines
                    for level in support_levels:
                        fig.add_shape(
                            type="line",
                            x0=0,
                            y0=level,
                            x1=1,
                            y1=level,
                            line=dict(
                                color="green",
                                width=2,
                                dash="dot",
                            ),
                        )
                    
                    # Add current price marker
                    fig.add_trace(
                        go.Scatter(
                            x=[0.5],
                            y=[current_stock_price],
                            mode="markers",
                            marker=dict(size=12, color="blue"),
                            name="Current Price"
                        )
                    )
                    
                    # Add labels for support levels
                    for i, level in enumerate(support_levels):
                        fig.add_annotation(
                            x=0.05,
                            y=level,
                            text=f"Support {i+1}: ${level:.2f}",
                            showarrow=False,
                            yshift=10,
                            font=dict(color="green")
                        )
                    
                    # Configure the layout
                    fig.update_layout(
                        title="Support Levels for Stop Loss Guidance",
                        xaxis=dict(
                            showticklabels=False,
                            showgrid=False,
                        ),
                        yaxis=dict(
                            title="Price ($)",
                            range=[
                                min(min(support_levels), current_stock_price) * 0.95,
                                max(max(support_levels), current_stock_price) * 1.05
                            ]
                        ),
                        height=400,
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Stop loss recommendations
                    st.subheader("Stop Loss Recommendations")
                    
                    # Find the closest support level below the current price
                    closest_support = None
                    for level in sorted(support_levels, reverse=True):
                        if level < current_stock_price:
                            closest_support = level
                            break
                    
                    if closest_support:
                        price_difference = current_stock_price - closest_support
                        percentage_difference = (price_difference / current_stock_price) * 100
                        
                        st.markdown(f"""
                        - **Closest Support Level**: ${closest_support:.2f} (${price_difference:.2f} or {percentage_difference:.1f}% below current price)
                        - **Conservative Stop Loss**: ${(closest_support * 0.98):.2f}
                        - **Aggressive Stop Loss**: ${(closest_support * 0.95):.2f}
                        """)
                    else:
                        st.warning("No support levels found below current price. Consider using a percentage-based stop loss.")
                
                # Disclaimer
                st.info(
                    "⚠️ **Disclaimer**: These calculations are estimates based on the Black-Scholes model "
                    "and historical volatility. Actual option prices may vary based on market conditions "
                    "and other factors. This is not financial advice."
                )
                
        except Exception as e:
            st.error(f"Error calculating option price: {str(e)}")

st.markdown("---")
with st.expander("How This Calculator Works"):
    st.markdown("""
    This calculator uses the Black-Scholes option pricing model and real-time market data to:

    1. **Retrieve current market data** for the specified stock and option
    2. **Calculate the current option price** based on real market data
    3. **Estimate the future option price** at your target date and price
    4. **Calculate potential profit or loss** for your option position
    5. **Identify technical support levels** to help with stop loss placement

    The calculator takes into account:
    - Current stock price and volatility
    - Time decay (theta)
    - Option strike price and type (call/put)
    - Days until target date and expiration
    """)