"""
Fix the moneyness labeling in polygon_integration.py
This script will update all occurrences of "in-the-money" to correctly check
if options are actually in-the-money or out-of-the-money based on strike price
and current stock price.
"""

import re

def fix_moneyness_labels():
    # Read the polygon_integration.py file
    with open('polygon_integration.py', 'r') as file:
        content = file.read()
    
    # First, update the bullish (calls) section - lines 1423-1432
    call_section_pattern = re.compile(
        r'(\s+# Try to extract the real strike price from the option symbol\n'
        r'\s+if \'symbol\' in main_contract:\n'
        r'\s+strike_price = extract_strike_from_symbol\(main_contract\[\'symbol\'\]\)\n'
        r'\s+if strike_price:\n'
        r'\s+)summary \+= f"in-the-money \(\{strike_price\}\) options expiring \{expiry_date\}, purchased \{timestamp_str if timestamp_str else \'2025-04-14\'\}\.\\n\\n"(\n'
        r'\s+else:\n'
        r'\s+)summary \+= f"in-the-money \(\{contract_parts\[1\]\}\) options expiring \{expiry_date\}, purchased \{timestamp_str if timestamp_str else \'2025-04-14\'\}\.\\n\\n"(\n'
        r'\s+else:\n'
        r'\s+)summary \+= f"in-the-money \(\{contract_parts\[1\]\}\) options expiring \{expiry_date\}, purchased \{timestamp_str if timestamp_str else \'2025-04-14\'\}\.\\n\\n"'
    )
    
    call_section_replacement = (
        r'\1# Determine if call option is in-the-money based on strike vs stock price\n'
        r'            stock_price = result_with_metadata.get(\'current_stock_price\', 0)\n'
        r'            moneyness = determine_moneyness(strike_price, stock_price, \'call\')\n'
        r'            summary += f"{moneyness} ({strike_price}) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else \'2025-04-14\'}.\n\n"\2'
        r'# Check moneyness for contract parts\n'
        r'            try:\n'
        r'                strike_from_parts = float(contract_parts[1])\n'
        r'                moneyness = determine_moneyness(strike_from_parts, result_with_metadata.get(\'current_stock_price\', 0), \'call\')\n'
        r'            except (ValueError, IndexError):\n'
        r'                moneyness = "in-the-money"  # Default if we can\'t determine\n'
        r'            summary += f"{moneyness} ({contract_parts[1]}) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else \'2025-04-14\'}.\n\n"\3'
        r'# Check moneyness for contract parts\n'
        r'            try:\n'
        r'                strike_from_parts = float(contract_parts[1])\n'
        r'                moneyness = determine_moneyness(strike_from_parts, result_with_metadata.get(\'current_stock_price\', 0), \'call\')\n'
        r'            except (ValueError, IndexError):\n'
        r'                moneyness = "in-the-money"  # Default if we can\'t determine\n'
        r'            summary += f"{moneyness} ({contract_parts[1]}) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else \'2025-04-14\'}.\n\n"'
    )
    
    # Update the bearish (puts) section - lines 1491-1500
    put_section_pattern = re.compile(
        r'(\s+# Try to extract the real strike price from the option symbol\n'
        r'\s+if \'symbol\' in main_contract:\n'
        r'\s+strike_price = extract_strike_from_symbol\(main_contract\[\'symbol\'\]\)\n'
        r'\s+if strike_price:\n'
        r'\s+)summary \+= f"in-the-money \(\{strike_price\}\) options expiring \{expiry_date\}, purchased \{timestamp_str if timestamp_str else \'2025-04-14\'\}\.\\n\\n"(\n'
        r'\s+else:\n'
        r'\s+)summary \+= f"in-the-money \(\{contract_parts\[1\]\}\) options expiring \{expiry_date\}, purchased \{timestamp_str if timestamp_str else \'2025-04-14\'\}\.\\n\\n"(\n'
        r'\s+else:\n'
        r'\s+)summary \+= f"in-the-money \(\{contract_parts\[1\]\}\) options expiring \{expiry_date\}, purchased \{timestamp_str if timestamp_str else \'2025-04-14\'\}\.\\n\\n"'
    )
    
    put_section_replacement = (
        r'\1# Determine if put option is in-the-money based on strike vs stock price\n'
        r'            stock_price = result_with_metadata.get(\'current_stock_price\', 0)\n'
        r'            moneyness = determine_moneyness(strike_price, stock_price, \'put\')\n'
        r'            summary += f"{moneyness} ({strike_price}) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else \'2025-04-14\'}.\n\n"\2'
        r'# Check moneyness for contract parts\n'
        r'            try:\n'
        r'                strike_from_parts = float(contract_parts[1])\n'
        r'                moneyness = determine_moneyness(strike_from_parts, result_with_metadata.get(\'current_stock_price\', 0), \'put\')\n'
        r'            except (ValueError, IndexError):\n'
        r'                moneyness = "in-the-money"  # Default if we can\'t determine\n'
        r'            summary += f"{moneyness} ({contract_parts[1]}) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else \'2025-04-14\'}.\n\n"\3'
        r'# Check moneyness for contract parts\n'
        r'            try:\n'
        r'                strike_from_parts = float(contract_parts[1])\n'
        r'                moneyness = determine_moneyness(strike_from_parts, result_with_metadata.get(\'current_stock_price\', 0), \'put\')\n'
        r'            except (ValueError, IndexError):\n'
        r'                moneyness = "in-the-money"  # Default if we can\'t determine\n'
        r'            summary += f"{moneyness} ({contract_parts[1]}) options expiring {expiry_date}, purchased {timestamp_str if timestamp_str else \'2025-04-14\'}.\n\n"'
    )
    
    # Update the "expiring soon" sections
    soon_call_pattern = r'summary \+= f"in-the-money \(\{contract_parts\[1\]\}\) options expiring soon, purchased \{timestamp_str if timestamp_str else \'2025-04-14\'\}\\.'
    soon_call_replacement = (
        r'try:\n'
        r'                    strike_from_parts = float(contract_parts[1])\n'
        r'                    moneyness = determine_moneyness(strike_from_parts, result_with_metadata.get(\'current_stock_price\', 0), \'call\')\n'
        r'                except (ValueError, IndexError):\n'
        r'                    moneyness = "in-the-money"  # Default if we can\'t determine\n'
        r'                summary += f"{moneyness} ({contract_parts[1]}) options expiring soon, purchased {timestamp_str if timestamp_str else \'2025-04-14\'}.'
    )
    
    soon_put_pattern = r'summary \+= f"in-the-money \(\{contract_parts\[1\]\}\) options expiring soon, purchased \{timestamp_str if timestamp_str else \'2025-04-14\'\}\\.'
    soon_put_replacement = (
        r'try:\n'
        r'                    strike_from_parts = float(contract_parts[1])\n'
        r'                    moneyness = determine_moneyness(strike_from_parts, result_with_metadata.get(\'current_stock_price\', 0), \'put\')\n'
        r'                except (ValueError, IndexError):\n'
        r'                    moneyness = "in-the-money"  # Default if we can\'t determine\n'
        r'                summary += f"{moneyness} ({contract_parts[1]}) options expiring soon, purchased {timestamp_str if timestamp_str else \'2025-04-14\'}.'
    )

    # Apply the changes
    content = call_section_pattern.sub(call_section_replacement, content)
    content = put_section_pattern.sub(put_section_replacement, content)
    
    # Update the "expiring soon" sections - find each one and replace it
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if "expiring soon" in line and "in-the-money" in line:
            # Check if this is in the bullish or bearish section
            if i > 0 and "bullish" in lines[i-400:i]:
                # This is in the bullish section, use call option
                lines[i] = soon_call_pattern.sub(soon_call_replacement, line)
            elif i > 0 and "bearish" in lines[i-400:i]:
                # This is in the bearish section, use put option
                lines[i] = soon_put_pattern.sub(soon_put_replacement, line)
    
    updated_content = '\n'.join(lines)
    
    # Write the updated content back
    with open('polygon_integration.py', 'w') as file:
        file.write(updated_content)
    
    print("Moneyness labeling fixed successfully.")

if __name__ == "__main__":
    fix_moneyness_labels()