#!/usr/bin/env python3
"""
Targeted test script to verify the formatting changes for unusual options activity
"""
import re
import json
from polygon_integration import get_simplified_unusual_activity_summary

def print_formatted_output(ticker="AAPL"):
    """Print the unusual options activity output for a specific ticker"""
    print(f"Getting unusual options activity for {ticker}...")
    
    # Set max options to a very small number to speed up processing
    import polygon_integration
    original_max = polygon_integration.max_options_to_process if hasattr(polygon_integration, 'max_options_to_process') else 50
    polygon_integration.max_options_to_process = 5
    
    # Get the summary
    summary = get_simplified_unusual_activity_summary(ticker)
    
    # Restore original value
    polygon_integration.max_options_to_process = original_max
    
    # Print the formatted output
    print("\n===== UNUSUAL OPTIONS ACTIVITY OUTPUT =====\n")
    print(summary[:1000])  # Only print first part to reduce output size
    
    # Find and extract the first bullet point
    first_bullet = re.search(r'• I\'m seeing.*?\.', summary)
    if first_bullet:
        formatted_line = first_bullet.group(0)
        print("\nExtracted first line for format checking:")
        print(formatted_line)
        
        # Check if our format changes are present
        checks = {
            "strongly": "strongly" in formatted_line,
            "Inc.": f"{ticker}, Inc." in formatted_line,
            "**$ million": "**$" in formatted_line and "million" in formatted_line,
            "in-the-money": "in-the-money" in summary,
            "($XX.XX)": re.search(r'\(\$\d+\.\d+\)', summary) is not None,
            "purchased": ", purchased" in summary
        }
        
        print("\nFormat checks:")
        for key, value in checks.items():
            print(f"  {'✅' if value else '❌'} {key}")
            
        if all(checks.values()):
            print("\n✅ All format requirements have been implemented!")
        else:
            print("\n❌ Some format requirements are missing. Further changes needed.")

if __name__ == "__main__":
    print_formatted_output("TSLA")