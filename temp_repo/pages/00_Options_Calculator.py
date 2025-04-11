import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
from option_calculator import calculate_option_price, get_option_chain, get_option_greeks
from technical_analysis import get_support_levels, get_stop_loss_recommendation
from unusual_activity import get_unusual_options_activity
from utils_file import validate_inputs, format_ticker
from utils.theme_helper import setup_page
from theme_selector import display_theme_selector

# Set page title and layout
st.set_page_config(
    page_title="Options Calculator",
    page_icon="📊",
    layout="wide"
)

# Display theme selector in sidebar
display_theme_selector()

# Title and description
st.title("Options Price Estimator")
st.markdown("""
This tool helps you estimate the future value of options based on a target stock price,
provides technical support-based stop loss recommendations, and highlights unusual options activity.
""")

# Sidebar for inputs
st.sidebar.header("Input Parameters")

# Stock ticker input
ticker_input = st.sidebar.text_input("Stock Symbol", "AAPL").upper()
ticker = format_ticker(ticker_input)

# Get current date and set default expiration date to 30 days from now
today = datetime.datetime.now().date()
default_expiry = today + datetime.timedelta(days=30)

# Error handling for stock data fetch
try:
    # Fetch stock data
    stock = yf.Ticker(ticker)
    info = stock.info
    
    # Display current stock info
    current_price = info.get('currentPrice', stock.history(period='1d')['Close'].iloc[-1])
    st.sidebar.markdown(f"**Current Price:** ${current_price:.2f}")
    
    # Get all available expiration dates
    try:
        expirations = stock.options
        if not expirations:
            st.warning(f"No options data available for {ticker}")
            st.stop()
            
        # Expiration date selection
        expiration_date = st.sidebar.selectbox(
            "Option Expiration Date",
            options=expirations,
            index=0 if expirations else None
        )
        
        # Option type selection
        option_type = st.sidebar.radio("Option Type", ["Call", "Put"])
        
        # Target price input
        target_price = st.sidebar.number_input(
            "Target Stock Price",
            min_value=0.01,
            max_value=float(current_price * 5),
            value=float(current_price * 1.1) if option_type == "Call" else float(current_price * 0.9),
            step=0.01
        )
        
        # Validate inputs
        validation_message = validate_inputs(ticker, target_price)
        if validation_message:
            st.sidebar.error(validation_message)
            st.stop()
        
        # Main content area
        st.header(f"{ticker} Option Analysis")
        
        # Show current stock information
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Price", f"${current_price:.2f}")
        with col2:
            daily_change = info.get('regularMarketChangePercent', 0)
            st.metric("Daily Change", f"{daily_change:.2f}%")
        with col3:
            volume = info.get('regularMarketVolume', 0)
            st.metric("Volume", f"{volume:,}")
        
        # Get option chain
        options_chain = get_option_chain(stock, expiration_date, option_type.lower())
        
        if options_chain.empty:
            st.warning(f"No {option_type.lower()} options available for {ticker} with expiration {expiration_date}")
            st.stop()
            
        # Display available strikes
        st.subheader("Available Strike Prices")
        
        # Calculate days to expiration
        expiry_date = datetime.datetime.strptime(expiration_date, '%Y-%m-%d').date()
        days_to_expiration = (expiry_date - today).days
        
        # Create columns for different sections
        option_col, estimate_col = st.columns(2)
        
        with option_col:
            # Strike price selection
            strike_prices = sorted(options_chain['strike'].unique())
            
            # Find closest strike to current price
            closest_strike_idx = min(range(len(strike_prices)), 
                                   key=lambda i: abs(strike_prices[i] - current_price))
            
            strike_price = st.selectbox(
                "Select Strike Price",
                options=strike_prices,
                index=closest_strike_idx
            )
            
            # Get selected option data
            selected_option = options_chain[options_chain['strike'] == strike_price].iloc[0]
            
            # Get option Greeks
            greeks = get_option_greeks(stock, expiration_date, strike_price, option_type.lower())
            
            # Display current option information
            st.subheader(f"Current Option Data ({option_type})")
            option_data = {
                "Strike Price": f"${strike_price:.2f}",
                "Current Option Price": f"${selected_option['lastPrice']:.2f}",
                "Bid": f"${selected_option['bid']:.2f}",
                "Ask": f"${selected_option['ask']:.2f}",
                "Volume": f"{selected_option['volume']:,}",
                "Open Interest": f"{selected_option['openInterest']:,}",
                "Implied Volatility": f"{selected_option['impliedVolatility']:.2%}",
                "Days to Expiration": f"{days_to_expiration} days"
            }
            
            option_df = pd.DataFrame(list(option_data.items()), columns=["Metric", "Value"])
            st.table(option_df)
            
            # Display Greeks
            st.subheader("Option Greeks")
            if greeks:
                greeks_data = {
                    "Delta": f"{greeks['delta']:.4f}",
                    "Gamma": f"{greeks['gamma']:.4f}",
                    "Theta": f"{greeks['theta']:.4f}",
                    "Vega": f"{greeks['vega']:.4f}"
                }
                greeks_df = pd.DataFrame(list(greeks_data.items()), columns=["Greek", "Value"])
                st.table(greeks_df)
                
                # Add tooltips for Greeks explanation
                st.info("""
                **Understanding Option Greeks:**
                - **Delta:** Sensitivity of option price to changes in underlying stock price
                - **Gamma:** Rate of change of Delta with respect to underlying price
                - **Theta:** Option price decay per day
                - **Vega:** Sensitivity to changes in implied volatility
                """)
            else:
                st.warning("Greeks data not available for this option")
        
        with estimate_col:
            # Calculate estimated option price
            estimated_price = calculate_option_price(
                current_price, 
                target_price, 
                strike_price, 
                greeks, 
                days_to_expiration,
                option_type.lower()
            )
            
            # Display estimated option price
            st.subheader("Option Price Estimation")
            st.metric(
                "Estimated Option Price at Target",
                f"${estimated_price:.2f}",
                f"{((estimated_price / selected_option['lastPrice']) - 1) * 100:.2f}%"
            )
            
            # Calculate profit/loss
            profit_loss = (estimated_price - selected_option['lastPrice']) * 100  # Per contract (100 shares)
            st.metric(
                "Estimated Profit/Loss per Contract",
                f"${profit_loss:.2f}",
                "Based on target price"
            )
            
            # Get stop loss recommendation
            stop_loss = get_stop_loss_recommendation(stock, current_price, option_type.lower())
            
            # Technical Support-based Stop Loss Recommendation
            st.subheader("Technical Support-Based Stop Loss")
            st.write(stop_loss["recommendation"])
            st.metric("Recommended Stop Loss Level", f"${stop_loss['level']:.2f}")
            
            # Risk assessment
            risk_reward_ratio = abs(profit_loss / ((selected_option['lastPrice'] - stop_loss.get('option_stop_price', 0)) * 100))
            
            if risk_reward_ratio > 0:
                st.metric("Risk/Reward Ratio", f"{risk_reward_ratio:.2f}")
                
                # Risk assessment
                if risk_reward_ratio > 3:
                    risk_assessment = "Favorable"
                    color = "green"
                elif risk_reward_ratio > 1:
                    risk_assessment = "Moderate"
                    color = "orange"
                else:
                    risk_assessment = "Unfavorable"
                    color = "red"
                    
                st.markdown(f"<p style='color:{color}'>Risk Assessment: {risk_assessment}</p>", unsafe_allow_html=True)
        
        # Unusual Options Activity
        st.header("Unusual Options Activity")
        
        try:
            unusual_activity = get_unusual_options_activity(ticker)
            
            if unusual_activity:
                # Create columns for bullish and bearish activity
                bullish_col, bearish_col = st.columns(2)
                
                with bullish_col:
                    st.subheader("Bullish Activity")
                    bullish_activity = [a for a in unusual_activity if a['sentiment'] == 'bullish']
                    if bullish_activity:
                        for activity in bullish_activity:
                            st.markdown(f"""
                            **Strike:** ${activity['strike']:.2f} | **Expiry:** {activity['expiry']}  
                            **Volume:** {activity['volume']:,} | **Open Interest:** {activity['open_interest']:,}  
                            **Amount:** ${activity['amount']:,.2f}
                            """)
                    else:
                        st.write("No significant bullish activity detected")
                
                with bearish_col:
                    st.subheader("Bearish Activity")
                    bearish_activity = [a for a in unusual_activity if a['sentiment'] == 'bearish']
                    if bearish_activity:
                        for activity in bearish_activity:
                            st.markdown(f"""
                            **Strike:** ${activity['strike']:.2f} | **Expiry:** {activity['expiry']}  
                            **Volume:** {activity['volume']:,} | **Open Interest:** {activity['open_interest']:,}  
                            **Amount:** ${activity['amount']:,.2f}
                            """)
                    else:
                        st.write("No significant bearish activity detected")
            else:
                st.info("No unusual options activity detected for this ticker")
        except Exception as e:
            st.error(f"Error fetching unusual options activity: {str(e)}")
            
    except Exception as e:
        st.error(f"Error loading options data: {str(e)}")
        
except Exception as e:
    st.error(f"Error fetching stock data for {ticker}: {str(e)}")
    st.info("Please check if the ticker symbol is correct and try again.")

# Add a footer with disclaimer
st.markdown("---")
st.markdown("""
**Disclaimer:** This tool provides estimates based on current market data and mathematical models.
Options trading involves significant risk, and actual results may vary. This is not financial advice.
Always do your own research before making investment decisions.
""")