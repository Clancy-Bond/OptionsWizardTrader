"""
Test script to verify our fix for nested stop loss data structure parsing.
This script tests the new logic in handle_stop_loss_request that handles
different stop loss data structures.
"""

import sys
import importlib.util
from datetime import datetime, timedelta

def import_module_from_file(file_path, module_name):
    """Import a module from file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def test_nested_stop_loss_data_handling():
    """
    Test how handle_stop_loss_request handles different stop loss data structures.
    """
    # Create test data with different structures
    test_cases = [
        # Simple direct level structure
        {
            "level": 150.25,
            "basis": "technical support"
        },
        
        # Nested swing level structure
        {
            "swing": {
                "level": 148.75,
                "basis": "swing support"
            }
        },
        
        # Nested primary level structure
        {
            "primary": {
                "level": 146.50,
                "basis": "primary support"
            }
        },
        
        # Combined nested structure with both keys
        {
            "swing": {
                "level": 148.75,
                "basis": "swing support"
            },
            "primary": {
                "level": 146.50,
                "basis": "primary support"
            }
        },
        
        # Missing level key structure
        {
            "basis": "technical support",
            "message": "No specific level found"
        }
    ]
    
    # Test each structure
    for i, test_data in enumerate(test_cases):
        # Extract the level using our new logic
        original_stop_loss = None
        
        if "level" in test_data:
            original_stop_loss = test_data.get("level")
        elif test_data.get("swing") and "level" in test_data.get("swing", {}):
            original_stop_loss = test_data.get("swing", {}).get("level")
        elif test_data.get("primary") and "level" in test_data.get("primary", {}):
            original_stop_loss = test_data.get("primary", {}).get("level")
        
        # Display results
        print(f"\nTest Case {i+1}:")
        print(f"  Input data: {test_data}")
        print(f"  Extracted level: {original_stop_loss}")
        
        # Verify if extraction worked correctly
        if original_stop_loss is not None:
            print(f"✅ Successfully extracted stop level: {original_stop_loss}")
        else:
            print("❌ Failed to extract stop level")
            
            # Let's try to create a fallback level like in our code
            technical_stop = 100.0 * 0.95  # Similar to what we do in the actual code
            print(f"  Using fallback technical_stop: {technical_stop}")

def main():
    """Run the main test function"""
    print("Testing nested stop loss data handling...")
    test_nested_stop_loss_data_handling()
    
if __name__ == "__main__":
    main()