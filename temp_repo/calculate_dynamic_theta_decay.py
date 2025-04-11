"""
This script contains functions to calculate dynamic theta decay over different time intervals
based on the trade horizon (scalp, swing, long-term).
"""

from datetime import datetime, timedelta

def calculate_dynamic_theta_decay(current_option_price, theta, expiration_date, trade_horizon="auto"):
    """
    Calculate theta decay projections with different intervals based on trade horizon.
    
    Args:
        current_option_price: Current price of the option
        theta: Theta value (daily decay)
        expiration_date: The expiration date of the option
        trade_horizon: "scalp", "swing", "longterm", or "auto" to determine based on days to expiration
        
    Returns:
        Dictionary with decay projections and formatting information
    """
    try:
        # Convert expiration_date to datetime if it's a string
        if isinstance(expiration_date, str):
            try:
                expiration_date = datetime.strptime(expiration_date, '%Y-%m-%d')
            except ValueError:
                # Try another format
                try:
                    expiration_date = datetime.strptime(expiration_date, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    # If parsing fails, don't use fallback data
                    raise ValueError(f"Unable to parse expiration date: {expiration_date}")
        
        # Calculate days to expiration
        today = datetime.now()
        if hasattr(expiration_date, 'date'):
            exp_date = expiration_date.date()
        else:
            exp_date = expiration_date
            
        if hasattr(today, 'date'):
            today_date = today.date()
        else:
            today_date = today
            
        try:
            days_to_expiration = (exp_date - today_date).days
            if days_to_expiration < 0:
                raise ValueError("Expiration date is in the past")
        except Exception as e:
            print(f"Error calculating days to expiration: {e}")
            raise ValueError("Unable to calculate days to expiration with valid date information")
        
        # Determine trade horizon if set to auto
        if trade_horizon == "auto":
            if days_to_expiration < 2:  # Less than 2 days = scalp
                trade_horizon = "scalp"
            elif days_to_expiration < 14:  # Less than 2 weeks = swing
                trade_horizon = "swing"
            else:  # 2+ weeks = long-term
                trade_horizon = "longterm"
        
        # Format expiration date for display - format as YYYY-MMM-DD with month in uppercase per requirements
        if hasattr(expiration_date, 'strftime'):
            # Format month as 3-letter abbreviation in uppercase (JAN, FEB, etc.)
            month_abbr = expiration_date.strftime('%b').upper()
            expiry_display = f"{expiration_date.strftime('%Y')}-{month_abbr}-{expiration_date.strftime('%d')}"
        else:
            # If it's a string format, try to parse and reformat
            try:
                # Try to parse different date formats
                if isinstance(expiration_date, str):
                    if '-' in expiration_date:
                        # Format like '2025-04-09'
                        year, month, day = expiration_date.split('-')
                        month_num = int(month)
                        month_names = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
                        month_abbr = month_names[month_num - 1]
                        expiry_display = f"{year}-{month_abbr}-{day}"
                    elif '/' in expiration_date:
                        # Format like '04/09/2025'
                        parts = expiration_date.split('/')
                        if len(parts) == 3:
                            if len(parts[2]) == 4:  # MM/DD/YYYY
                                month, day, year = parts
                            else:  # YYYY/MM/DD
                                year, month, day = parts
                                
                            month_num = int(month)
                            month_names = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
                            month_abbr = month_names[month_num - 1]
                            expiry_display = f"{year}-{month_abbr}-{day.zfill(2)}"
                        else:
                            expiry_display = str(expiration_date)
                    else:
                        expiry_display = str(expiration_date)
                else:
                    expiry_display = str(expiration_date)
            except:
                # If parsing fails, just use the string as is
                expiry_display = str(expiration_date)
        
        # Set time interval based on trade horizon
        if trade_horizon == "scalp":
            # For scalp trades, use hourly intervals (1/24 of a day)
            interval_days = 1/24  # 1 hour = 1/24 of a day
            num_intervals = 5  # Show 5 hourly intervals
            interval_text = "hour"
        elif trade_horizon == "swing":
            # For swing trades, use daily intervals (changed from 2-day to 1-day)
            interval_days = 1
            num_intervals = min(5, max(1, days_to_expiration))  # Ensure at least 1 interval even for 0 DTE
            interval_text = "day"
        else:  # longterm
            interval_days = 7
            # Handle the case where days_to_expiration is 0 (same-day expiration)
            if days_to_expiration == 0:
                num_intervals = 1  # At least show one interval
            else:
                num_intervals = min(4, max(1, days_to_expiration // 7))  # Reduced from 5 to 4 weeks
            interval_text = "week"
        
        # If we can't show at least 3 intervals, adjust to show at least 3
        # But skip this for 0 DTE options where we'll use hourly intervals
        if num_intervals < 3 and days_to_expiration >= 3:
            interval_days = days_to_expiration // 3
            num_intervals = 3
            interval_text = f"{interval_days}-day"
            
        # Special handling for 0 DTE options - always use hourly intervals
        if days_to_expiration == 0:
            interval_days = 1/24  # 1 hour = 1/24 of a day
            num_intervals = 5  # Show 5 hourly intervals (remaining hours until market close)
            interval_text = "hour"
            trade_horizon = "scalp"  # Force scalp trade horizon for 0 DTE
        
        # Calculate decay for each interval
        projections = []
        projected_price = current_option_price
        
        for i in range(1, num_intervals + 1):
            # Calculate days for this interval
            days = i * interval_days
            date = today + timedelta(days=days)
            
            # Calculate decay for this period - scale appropriately for time intervals
            # For hourly decay (scalp trades), divide the daily theta by 24 and then multiply by hours
            # For daily/weekly decay, multiply theta by days as usual
            # Theta is typically negative (representing decay), so we use the absolute value for calculations
            # and then subtract from the price
            interval_decay = abs(theta) * interval_days
            
            # Calculate percentage changes - protect against division by zero
            if projected_price > 0:
                interval_percentage = (interval_decay / projected_price) * 100
                # Ensure we have a minimum visible percentage for small decays (at least 0.1%)
                if interval_percentage > 0 and interval_percentage < 0.1:
                    interval_percentage = 0.1
            else:
                interval_percentage = 0.1  # Default minimum percentage
                
            if current_option_price > 0:
                cumulative_percentage = (interval_decay * i / current_option_price) * 100
                # Ensure we have a minimum visible percentage for small decays (at least 0.1%)
                if cumulative_percentage > 0 and cumulative_percentage < 0.1:
                    cumulative_percentage = 0.1 * i  # Scale by interval to show progression
            else:
                cumulative_percentage = 0.1 * i  # Default minimum percentage
            
            # Update projected price (ensure it doesn't go below 0.01)
            # Theta represents decay, so we SUBTRACT the decay from the price
            projected_price = max(0.01, projected_price - interval_decay)
            
            # Format date based on interval type
            if trade_horizon == "scalp":
                # Calculate actual market hours for scalp trades
                # Start with current time
                current_time = datetime.now()
                # Add the hours for this interval
                future_time = current_time + timedelta(hours=i)
                
                # Format the time in 12-hour format with AM/PM
                hour_12 = future_time.hour % 12
                if hour_12 == 0:
                    hour_12 = 12
                am_pm = "AM" if future_time.hour < 12 else "PM"
                
                # Create the complete timestamp with month abbreviation in uppercase
                month_abbr = future_time.strftime('%b').upper()
                date_str = f"{future_time.strftime('%Y')}-{month_abbr}-{future_time.strftime('%d')} {hour_12}:00 {am_pm}"
            else:
                # For swing and long-term trades, just show the date with month in uppercase
                month_abbr = date.strftime('%b').upper()
                date_str = f"{date.strftime('%Y')}-{month_abbr}-{date.strftime('%d')}"
            
            projections.append({
                'interval': i,
                'date': date_str,
                'projected_price': projected_price,
                'interval_percentage': interval_percentage,
                'cumulative_percentage': cumulative_percentage
            })
        
        # Format the projection text based on trade horizon type
        # Simple introductory text per user request - no extra newline
        projection_text = "Assuming stationary price:\n"
        
        for proj in projections:
            if trade_horizon == "scalp":
                # For scalp trades, show hour intervals
                interval_name = f"Hour {proj['interval']}"
            elif trade_horizon == "swing":
                # For swing trades, show daily intervals
                interval_name = f"Day {int(proj['interval'])}"
            else:  # longterm
                # For long-term trades, show Week 1, Week 2, etc.
                interval_name = f"Week {int(proj['interval'])}"
                
            projection_text += f"{interval_name} ({proj['date']}): ${proj['projected_price']:.2f} "
            
            # Different wording based on trade horizon
            if trade_horizon == "scalp":
                projection_text += f"({proj['interval_percentage']:.1f}% hourly decay, {proj['cumulative_percentage']:.1f}% total)\n"
            elif trade_horizon == "swing":
                projection_text += f"({proj['interval_percentage']:.1f}% daily decay, {proj['cumulative_percentage']:.1f}% total)\n"
            else:  # longterm
                projection_text += f"({proj['interval_percentage']:.1f}% weekly decay, {proj['cumulative_percentage']:.1f}% total)\n"
        
        # Exit strategy message removed per request
        
        return {
            "expiry_display": expiry_display,
            "trade_horizon": trade_horizon,
            "projection_text": projection_text,
            "days_to_expiration": days_to_expiration,
            "projections": projections
        }
        
    except Exception as e:
        print(f"Error calculating dynamic theta decay: {str(e)}")
        # Return an error message without synthetic data
        return {
            "error": "Unable to calculate theta decay projections with current market data",
            "data_available": False
        }

def format_theta_decay_field(decay_data):
    """
    Format theta decay data for display in a Discord embed field
    
    Args:
        decay_data: The data returned from calculate_dynamic_theta_decay
        
    Returns:
        Dictionary with name and value for the embed field
    """
    try:
        # Check if the data contains an error message
        if decay_data.get('data_available') is False:
            return {
                "name": "⏳ THETA DECAY PROJECTION UNAVAILABLE ⏳",
                "value": decay_data.get('error', "Could not calculate theta decay projections with current market data.")
            }
        
        # No error, proceed with normal formatting
        field_name = f"⏳ THETA DECAY PROJECTION TO ({decay_data['expiry_display']}) ⏳"
        field_value = decay_data['projection_text']
        
        return {
            "name": field_name,
            "value": field_value
        }
    except Exception as e:
        print(f"Error formatting theta decay field: {str(e)}")
        return {
            "name": "⏳ THETA DECAY PROJECTION ERROR ⏳",
            "value": "Error formatting theta decay projections. No synthetic data provided."
        }

# For testing
if __name__ == "__main__":
    # Example usage
    current_price = 5.45
    theta = -0.15
    expiration = "2025-06-20"
    
    # Test all three horizons
    horizons = ["scalp", "swing", "longterm"]
    for horizon in horizons:
        decay_data = calculate_dynamic_theta_decay(current_price, theta, expiration, horizon)
        field = format_theta_decay_field(decay_data)
        print(f"\n=== {horizon.upper()} ===")
        print(f"Field Name: {field['name']}")
        print(f"Field Value:\n{field['value']}")