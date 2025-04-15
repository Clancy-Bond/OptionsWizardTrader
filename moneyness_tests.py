"""
Test the moneyness detection functionality to ensure it correctly identifies
in-the-money and out-of-the-money options based on strike price and stock price.
"""

def test_determine_moneyness():
    """Test the determine_moneyness function with various inputs"""
    from polygon_integration import determine_moneyness
    
    # Test cases for call options
    assert determine_moneyness(100, 120, 'call') == 'in-the-money'
    assert determine_moneyness(120, 100, 'call') == 'out-of-the-money'
    assert determine_moneyness('100', 120, 'call') == 'in-the-money'
    assert determine_moneyness('120', 100, 'call') == 'out-of-the-money'
    
    # Test cases for put options
    assert determine_moneyness(100, 80, 'put') == 'in-the-money'
    assert determine_moneyness(80, 100, 'put') == 'out-of-the-money'
    assert determine_moneyness('100', 80, 'put') == 'in-the-money'
    assert determine_moneyness('80', 100, 'put') == 'out-of-the-money'
    
    # Test cases for invalid inputs
    assert determine_moneyness('invalid', 100, 'call') == 'in-the-money'
    assert determine_moneyness(100, 0, 'call') == 'out-of-the-money'
    assert determine_moneyness(100, None, 'put') == 'in-the-money'
    
    print("All moneyness tests passed!")

if __name__ == "__main__":
    test_determine_moneyness()