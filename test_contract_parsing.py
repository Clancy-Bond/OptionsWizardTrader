"""
Script to test and debug the contract parsing in unusual activity
"""
import json
from polygon_integration import get_unusual_options_activity

# Use a ticker with known options activity
ticker = "TSLA"

# Get the full unusual activity data
data = get_unusual_options_activity(ticker)

# Check if we have activity data
if data and 'activity' in data and len(data['activity']) > 0:
    # Print the first activity item to see its structure
    print("\nFirst activity item:")
    first_item = data['activity'][0]
    print(json.dumps(first_item, indent=2))
    
    # Print the contract string if available
    if 'contract' in first_item:
        print("\nContract string:", first_item['contract'])
        contract_parts = first_item['contract'].split()
        print("Contract parts:", contract_parts)
        
        if len(contract_parts) >= 3:
            print(f"Strike: {contract_parts[0]}")
            print(f"Moneyness: {contract_parts[1]}")
            print(f"Expiry: {contract_parts[2]}")
            
            # This is what gets displayed in the output
            formatted = f"{contract_parts[1]}-the-money (${contract_parts[0]})"
            print(f"Formatted in output: {formatted}")
            
            # Proposed fix
            fixed_format = f"${contract_parts[0]} {contract_parts[1]}-the-money"
            print(f"Proposed fix: {fixed_format}")
else:
    print("No unusual activity data found.")