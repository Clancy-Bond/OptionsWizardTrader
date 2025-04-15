"""
Apply moneyness fixes to polygon_integration.py
This script edits polygon_integration.py to use determine_moneyness()
"""

with open('polygon_integration.py', 'r') as file:
    lines = file.readlines()

# For Call options (bullish section) - around line 1427
for i in range(len(lines)):
    if "summary += f\"in-the-money ({strike_price}) options expiring {expiry_date}," in lines[i]:
        # Get the indentation
        indent = lines[i].split('summary')[0]
        # Determine if this is in the bullish or bearish section
        option_type = 'call'
        look_back = ''.join(lines[max(0, i-100):i])
        if "overall_sentiment == \"bearish\"" in look_back:
            option_type = 'put'
        
        # Replace the line with proper moneyness detection
        lines[i] = f"{indent}# Determine correct moneyness\n"
        lines[i] += f"{indent}stock_price = result_with_metadata.get('current_stock_price', 0)\n"
        lines[i] += f"{indent}moneyness = determine_moneyness(strike_price, stock_price, '{option_type}')\n"
        lines[i] += f"{indent}summary += f\"{{moneyness}} ({{strike_price}}) options expiring {{expiry_date}}, purchased {{timestamp_str if timestamp_str else '2025-04-14'}}.\n\n\"\n"
    
    # For contract_parts version
    elif "summary += f\"in-the-money ({contract_parts[1]}) options expiring {expiry_date}," in lines[i]:
        # Get the indentation
        indent = lines[i].split('summary')[0]
        # Determine if this is in the bullish or bearish section
        option_type = 'call'
        look_back = ''.join(lines[max(0, i-100):i])
        if "overall_sentiment == \"bearish\"" in look_back:
            option_type = 'put'
        
        # Replace the line with proper moneyness detection
        lines[i] = f"{indent}# Try to determine moneyness from contract parts\n"
        lines[i] += f"{indent}try:\n"
        lines[i] += f"{indent}    strike_from_parts = float(contract_parts[1])\n"
        lines[i] += f"{indent}    moneyness = determine_moneyness(strike_from_parts, result_with_metadata.get('current_stock_price', 0), '{option_type}')\n"
        lines[i] += f"{indent}except (ValueError, IndexError):\n"
        lines[i] += f"{indent}    moneyness = \"in-the-money\"  # Default if we can't determine\n"
        lines[i] += f"{indent}summary += f\"{{moneyness}} ({{contract_parts[1]}}) options expiring {{expiry_date}}, purchased {{timestamp_str if timestamp_str else '2025-04-14'}}.\n\n\"\n"
    
    # For "expiring soon" versions
    elif "summary += f\"in-the-money ({contract_parts[1]}) options expiring soon, purchased" in lines[i]:
        # Get the indentation
        indent = lines[i].split('summary')[0]
        # Determine if this is in the bullish or bearish section
        option_type = 'call'
        look_back = ''.join(lines[max(0, i-100):i])
        if "overall_sentiment == \"bearish\"" in look_back:
            option_type = 'put'
        
        # Replace the line with proper moneyness detection
        lines[i] = f"{indent}# Try to determine moneyness for soon-expiring options\n"
        lines[i] += f"{indent}try:\n"
        lines[i] += f"{indent}    strike_from_parts = float(contract_parts[1])\n"
        lines[i] += f"{indent}    moneyness = determine_moneyness(strike_from_parts, result_with_metadata.get('current_stock_price', 0), '{option_type}')\n"
        lines[i] += f"{indent}except (ValueError, IndexError):\n"
        lines[i] += f"{indent}    moneyness = \"in-the-money\"  # Default if we can't determine\n"
        lines[i] += f"{indent}summary += f\"{{moneyness}} ({{contract_parts[1]}}) options expiring soon, purchased {{timestamp_str if timestamp_str else '2025-04-14'}}.\n\n\"\n"

with open('polygon_integration.py', 'w') as file:
    file.writelines(lines)

print("Moneyness fixes applied successfully!")