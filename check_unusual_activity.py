"""
Check how unusual options activity is detected and where transaction dates come from
"""
import os
import json
import re
from datetime import datetime
import requests
from dotenv import load_dotenv
from polygon_integration import get_unusual_options_activity, get_simplified_unusual_activity_summary

def get_unusual_options_activity_direct(ticker):
    """
    Directly query Polygon API for options activity data
    """
    # Get the unusual activity
    activity = get_unusual_options_activity(ticker)
    
    if not activity:
        print(f"No unusual activity found for {ticker}")
        return
    
    print(f"Found {len(activity)} unusual activities for {ticker}")
    
    # Print the first bullish and first bearish option (if available)
    bullish = next((item for item in activity if item.get('sentiment') == 'bullish'), None)
    bearish = next((item for item in activity if item.get('sentiment') == 'bearish'), None)
    
    if bullish:
        print("\n----- BULLISH OPTION -----")
        print(f"Contract: {bullish.get('contract')}")
        print(f"Unusualness Score: {bullish.get('unusualness_score')}")
        if 'timestamp_human' in bullish:
            print(f"Timestamp: {bullish.get('timestamp_human')}")
        print(f"Volume: {bullish.get('volume')}")
        print(f"Premium: ${bullish.get('premium'):,.2f}")
    
    if bearish:
        print("\n----- BEARISH OPTION -----")
        print(f"Contract: {bearish.get('contract')}")
        print(f"Unusualness Score: {bearish.get('unusualness_score')}")
        if 'timestamp_human' in bearish:
            print(f"Timestamp: {bearish.get('timestamp_human')}")
        print(f"Volume: {bearish.get('volume')}")
        print(f"Premium: ${bearish.get('premium'):,.2f}")
    
    # Get and print the simplified summary
    print("\n----- SIMPLIFIED SUMMARY -----")
    summary = get_simplified_unusual_activity_summary(ticker)
    print(summary)
    
    # Check if the timestamps match
    bullish_timestamp_pattern = r"Largest bullish trade occurred at: (.*?)\n"
    bearish_timestamp_pattern = r"Largest bearish trade occurred at: (.*?)\n"
    
    bullish_timestamp_match = re.search(bullish_timestamp_pattern, summary)
    bearish_timestamp_match = re.search(bearish_timestamp_pattern, summary)
    
    if bullish_timestamp_match and bullish:
        bullish_summary_timestamp = bullish_timestamp_match.group(1)
        print("\n✅ VERIFICATION - BULLISH:")
        print(f"From raw data: {bullish.get('timestamp_human')}")
        print(f"From summary: {bullish_summary_timestamp}")
        if bullish.get('timestamp_human') == bullish_summary_timestamp:
            print("✅ Timestamps match!")
        else:
            print("❌ Timestamps don't match")
    
    if bearish_timestamp_match and bearish:
        bearish_summary_timestamp = bearish_timestamp_match.group(1)
        print("\n✅ VERIFICATION - BEARISH:")
        print(f"From raw data: {bearish.get('timestamp_human')}")
        print(f"From summary: {bearish_summary_timestamp}")
        if bearish.get('timestamp_human') == bearish_summary_timestamp:
            print("✅ Timestamps match!")
        else:
            print("❌ Timestamps don't match")

if __name__ == "__main__":
    get_unusual_options_activity_direct("SPY")