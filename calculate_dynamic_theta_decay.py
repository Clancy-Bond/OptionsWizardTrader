import datetime

def project_theta_decay(current_price, theta, days_to_expiration):
    """
    Project option value decay over time based on theta
    
    Args:
        current_price (float): Current option price
        theta (float): Daily theta value (negative for typical options)
        days_to_expiration (int): Days to expiration
    
    Returns:
        str: Formatted string with theta decay projection
    """
    # Determine appropriate interval based on DTE
    if days_to_expiration <= 2:  # Scalp trade
        interval = 'hourly'
        num_intervals = min(days_to_expiration * 6, 12)  # Show up to 12 hourly intervals
    elif days_to_expiration <= 90:  # Swing trade
        interval = 'daily'
        num_intervals = min(days_to_expiration, 7)  # Show up to 7 daily intervals
    else:  # Long-term trade
        interval = 'weekly'
        num_intervals = min(days_to_expiration // 7, 8)  # Show up to 8 weekly intervals
    
    # Generate decay projection
    decay_projection = []
    today = datetime.date.today()
    
    if interval == 'hourly':
        # For hourly, theta is daily, so divide by ~6 trading hours
        hourly_theta = theta / 6
        for i in range(1, num_intervals + 1):
            hours_from_now = i
            price_estimate = max(0, current_price + hourly_theta * hours_from_now)
            time_str = f"{hours_from_now} hour{'s' if hours_from_now > 1 else ''}"
            decay_projection.append(f"T+{time_str}: ${price_estimate:.2f}")
    
    elif interval == 'daily':
        for i in range(1, num_intervals + 1):
            days_from_now = i
            date = today + datetime.timedelta(days=days_from_now)
            price_estimate = max(0, current_price + theta * days_from_now)
            date_str = date.strftime("%a %m/%d")
            decay_projection.append(f"{date_str}: ${price_estimate:.2f}")
    
    else:  # weekly
        for i in range(1, num_intervals + 1):
            weeks_from_now = i
            days_from_now = weeks_from_now * 7
            date = today + datetime.timedelta(days=days_from_now)
            price_estimate = max(0, current_price + theta * days_from_now)
            date_str = date.strftime("%m/%d")
            decay_projection.append(f"Week {weeks_from_now} ({date_str}): ${price_estimate:.2f}")
    
    # Format the output
    if interval == 'hourly':
        header = "⏱️ Hourly Theta Decay"
    elif interval == 'daily':
        header = "📅 Daily Theta Decay"
    else:
        header = "📆 Weekly Theta Decay"
    
    result = header + "\n" + "\n".join(decay_projection)
    return result
