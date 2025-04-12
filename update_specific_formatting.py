#!/usr/bin/env python3
"""
Script to update specific lines in polygon_integration.py for correct formatting
"""

def update_file():
    """Apply targeted formatting changes to specific sections"""
    # Read the file
    with open('polygon_integration.py', 'r') as file:
        lines = file.readlines()
    
    # Define the line numbers and updated content
    updates = {
        # Line 1036: Bold "million bullish" in first occurrence
        1036: '                summary += f"• I\'m seeing strongly bullish activity for {ticker}, Inc.. The largest flow is a ${premium_in_millions:.1f} **million bullish** bet that\\n"\n',
        
        # Line 1037: Change "at" to "on" and format timestamp
        1037: '                summary += f"occurred on {timestamp_str.split()[0]} with "\n',
        
        # Line 1039: Bold "million bullish" in second occurrence
        1039: '                summary += f"• I\'m seeing strongly bullish activity for {ticker}, Inc.. The largest flow is a ${premium_in_millions:.1f} **million bullish**\\n"\n',
        
        # Line 1046: Fix in-the-money formatting
        1046: '                    summary += f"in-the-money (${contract_parts[0]}.00) options expiring on {expiry_date}.\\n\\n"\n',
        
        # Line 1048: Fix in-the-money formatting
        1048: '                    # Fallback to just the second part if we couldn\'t parse a proper date\n                    summary += f"in-the-money (${contract_parts[0]}.00) options expiring soon.\\n\\n"\n',
        
        # Line 1055: Bold "million bullish" in error handler
        1055: '                summary += f"• I\'m seeing strongly bullish activity for {ticker}, Inc.. The largest flow is a ${premium_in_millions:.1f} **million bullish** bet that\\n"\n',
        
        # Line 1056: Change "at" to "on" and format timestamp
        1056: '                summary += f"occurred on {timestamp_str.split()[0]} with options from the largest unusual activity.\\n\\n"\n',
        
        # Line 1058: Bold "million bullish" in error handler fallback
        1058: '                summary += f"• I\'m seeing strongly bullish activity for {ticker}, Inc.. The largest flow is a ${premium_in_millions:.1f} **million bullish**\\n"\n',
        
        # Line 1092: Bold "million bearish" in bearish occurrence
        1092: '                summary += f"• I\'m seeing strongly bearish activity for {ticker}, Inc.. The largest flow is a ${premium_in_millions:.1f} **million bearish** bet that\\n"\n',
        
        # Line 1093: Change "at" to "on" and format timestamp
        1093: '                summary += f"occurred on {timestamp_str.split()[0]} with "\n',
        
        # Line 1095: Bold "million bearish" in second bearish occurrence
        1095: '                summary += f"• I\'m seeing strongly bearish activity for {ticker}, Inc.. The largest flow is a ${premium_in_millions:.1f} **million bearish**\\n"\n',
        
        # Line 1102: Fix in-the-money formatting
        1102: '                    summary += f"in-the-money (${contract_parts[0]}.00) options expiring on {expiry_date}.\\n\\n"\n',
        
        # Line 1104: Fix in-the-money formatting
        1104: '                    # Fallback to just the second part if we couldn\'t parse a proper date\n                    summary += f"in-the-money (${contract_parts[0]}.00) options expiring soon.\\n\\n"\n',
        
        # Line 1111: Bold "million bearish" in error handler
        1111: '                summary += f"• I\'m seeing strongly bearish activity for {ticker}, Inc.. The largest flow is a ${premium_in_millions:.1f} **million bearish** bet that\\n"\n',
        
        # Line 1112: Change "at" to "on" and format timestamp
        1112: '                summary += f"occurred on {timestamp_str.split()[0]} with options from the largest unusual activity.\\n\\n"\n',
        
        # Line 1114: Bold "million bearish" in error handler fallback
        1114: '                summary += f"• I\'m seeing strongly bearish activity for {ticker}, Inc.. The largest flow is a ${premium_in_millions:.1f} **million bearish**\\n"\n'
    }
    
    # Apply the updates
    for line_number, new_content in updates.items():
        # Line numbers in the dictionary are 1-indexed, arrays are 0-indexed
        if 0 <= line_number - 1 < len(lines):
            lines[line_number - 1] = new_content
    
    # Write the updated content back to the file
    with open('polygon_integration.py', 'w') as file:
        file.writelines(lines)
    
    print("Updated specific lines in polygon_integration.py with correct formatting")

if __name__ == "__main__":
    update_file()