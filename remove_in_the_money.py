"""
Quick script to remove all instances of "in-the-money" from polygon_integration.py
"""

def remove_in_the_money():
    with open('polygon_integration.py', 'r') as file:
        content = file.read()
    
    # Replace "in-the-money " with an empty string
    modified_content = content.replace("in-the-money ", "")
    
    with open('polygon_integration.py', 'w') as file:
        file.write(modified_content)
    
    print('Removed all instances of "in-the-money" from polygon_integration.py')

if __name__ == "__main__":
    remove_in_the_money()