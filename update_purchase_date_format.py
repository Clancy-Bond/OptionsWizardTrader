"""
Update the purchase date format to match the ISO standard format (YYYY-MM-DD)
"""

import datetime

def update_purchase_date_format():
    print("Updating purchase date format to YYYY-MM-DD...")
    
    with open('polygon_integration.py', 'r') as file:
        content = file.read()
    
    # Get today's date in ISO format to use as a default
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # Update the fallback purchase date format in bullish and bearish sections
    # Original: timestamp_str if timestamp_str else '04/11/25'
    updated_content = content.replace(
        "purchased {timestamp_str if timestamp_str else '04/11/25'}", 
        f"purchased {{timestamp_str if timestamp_str else '{today}'}}"
    )
    
    # Write the modified content back to the file
    with open('polygon_integration.py', 'w') as file:
        file.write(updated_content)
    
    print(f"Purchase date format updated to use ISO date format (example: {today})!")

if __name__ == "__main__":
    update_purchase_date_format()