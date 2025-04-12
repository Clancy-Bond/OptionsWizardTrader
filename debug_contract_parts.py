#!/usr/bin/env python3
"""
Debug script to see what contract_parts contains for TSLA unusual activity
"""
import json
import re
from polygon_integration import get_unusual_options_activity

ticker = "TSLA"

# Get unusual options activity data
activity = get_unusual_options_activity(ticker)

if activity and len(activity) > 0:
    print(f"\n===== Found {len(activity)} unusual options activities for {ticker} =====\n")
    
    # Look at the first item in the activity list
    main_contract = next((item for item in activity if item.get('sentiment') == 'bullish'), activity[0])
    print("Main contract data:")
    print(json.dumps(main_contract, indent=2))
    
    # Check the contract parts
    contract_str = main_contract.get('contract', '')
    contract_parts = contract_str.split()
    
    print(f"\nContract string: {contract_str}")
    print(f"Contract parts after splitting: {contract_parts}")
    
    if len(contract_parts) >= 1:
        print(f"\nFirst contract part: {contract_parts[0]}")
        
        # Check if it's a valid strike price or the ticker itself
        if re.match(r'^\d+(\.\d+)?$', contract_parts[0]):
            print("✅ First part is a valid number (strike price)")
        elif contract_parts[0] == ticker:
            print("❌ First part is the ticker symbol instead of strike price")
        else:
            print(f"❓ First part is neither a number nor the ticker: {contract_parts[0]}")
        
    if len(contract_parts) >= 3:
        print(f"Expiry date from parts: {contract_parts[2]}")
else:
    print(f"No unusual options activity found for {ticker}")