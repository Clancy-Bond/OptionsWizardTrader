import re
import os
import json
from datetime import datetime, timedelta

def format_ticker(ticker):
    """
    Format ticker symbol to be compatible with yfinance.
    
    Args:
        ticker: Ticker symbol input
    
    Returns:
        Formatted ticker symbol
    """
    # Remove any whitespace
    ticker = ticker.strip().upper()
    
    # Replace any special characters except dots
    ticker = re.sub(r'[^A-Z0-9\.]', '', ticker)
    
    # Check if it's a valid ticker format
    if not ticker or len(ticker) > 10:
        return 'AAPL'  # Default to AAPL if invalid
    
    return ticker

def validate_inputs(ticker, target_price=None):
    """
    Validate user inputs.
    
    Args:
        ticker: Stock ticker symbol
        target_price: Target stock price (optional)
    
    Returns:
        Error message if validation fails, None otherwise
    """
    if not ticker or len(ticker) > 10:
        return "Please enter a valid ticker symbol."
    
    if target_price is not None and target_price <= 0:
        return "Target price must be greater than zero."
    
    return None

def parse_relative_date(date_text):
    """
    Parse relative date references like 'next Friday', 'tomorrow', etc.
    
    Args:
        date_text: Text containing relative date reference
    
    Returns:
        Date in YYYY-MM-DD format or None if parsing fails
    """
    date_text = date_text.lower()
    today = datetime.now().date()
    
    if 'tomorrow' in date_text:
        target_date = today + timedelta(days=1)
        return target_date.strftime('%Y-%m-%d')
    
    if 'today' in date_text:
        return today.strftime('%Y-%m-%d')
        
    if 'next week' in date_text:
        target_date = today + timedelta(days=7)
        return target_date.strftime('%Y-%m-%d')
        
    if 'next month' in date_text:
        # Approximate a month as 30 days
        target_date = today + timedelta(days=30)
        return target_date.strftime('%Y-%m-%d')
        
    # Check for days of the week
    days = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 
        'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
    }
    
    for day, day_num in days.items():
        if day in date_text:
            # Calculate days until the next occurrence of this day
            current_day_num = today.weekday()
            days_ahead = (day_num - current_day_num) % 7
            
            # If "next" is specified and it's the same day of the week, add a week
            if 'next' in date_text and days_ahead == 0:
                days_ahead = 7
            
            # If it's the same day but without "next", use today's date
            if days_ahead == 0 and 'next' not in date_text:
                return today.strftime('%Y-%m-%d')
                
            # Calculate the target date
            target_date = today + timedelta(days=days_ahead)
            return target_date.strftime('%Y-%m-%d')
    
    return None

def load_permissions():
    """
    Load bot permissions from JSON file
    
    Returns:
        Dictionary of permissions
    """
    permissions = {}
    try:
        if os.path.exists("discord_permissions.json"):
            with open("discord_permissions.json", "r") as f:
                permissions = json.load(f)
    except Exception as e:
        print(f"Error loading permissions: {str(e)}")
    
    return permissions