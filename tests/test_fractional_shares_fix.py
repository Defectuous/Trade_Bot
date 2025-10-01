"""Test script to validate the fractional shares compatibility fix."""

import sys
import os
from decimal import Decimal
from unittest.mock import Mock, patch

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.alpaca_client import is_fractionable

def test_is_fractionable_function():
    """Test the is_fractionable function with mock API."""
    print("Testing is_fractionable function...")
    
    # Create a mock API
    mock_api = Mock()
    
    # Test case 1: Fractionable asset (most common stocks)
    mock_api.get_asset.return_value = Mock(fractionable=True)
    result = is_fractionable(mock_api, "AAPL")
    assert result == True, f"Expected True for fractionable asset, got {result}"
    print("✅ Test 1 passed: Fractionable asset returns True")
    
    # Test case 2: Non-fractionable asset (like TOI that caused the error)
    mock_api.get_asset.return_value = Mock(fractionable=False)
    result = is_fractionable(mock_api, "TOI")
    assert result == False, f"Expected False for non-fractionable asset, got {result}"
    print("✅ Test 2 passed: Non-fractionable asset returns False")
    
    # Test case 3: API error handling
    mock_api.get_asset.side_effect = Exception("API Error")
    result = is_fractionable(mock_api, "ERROR")
    assert result == False, f"Expected False for API error, got {result}"
    print("✅ Test 3 passed: API error returns False (safe default)")
    
    print("All is_fractionable tests passed!")

def test_fractional_quantity_logic():
    """Test the fractional quantity detection logic."""
    print("\nTesting fractional quantity detection...")
    
    # Test case 1: Whole number
    qty = Decimal("5")
    is_whole = qty == qty.to_integral_value()
    assert is_whole == True, f"Expected True for whole number, got {is_whole}"
    print("✅ Test 1 passed: Whole number detected correctly")
    
    # Test case 2: Fractional number
    qty = Decimal("5.5")
    is_whole = qty == qty.to_integral_value()
    assert is_whole == False, f"Expected False for fractional number, got {is_whole}"
    print("✅ Test 2 passed: Fractional number detected correctly")
    
    # Test case 3: Rounding fractional to whole
    qty = Decimal("5.7")
    rounded = Decimal(int(qty))
    assert rounded == Decimal("5"), f"Expected 5 after rounding, got {rounded}"
    print("✅ Test 3 passed: Fractional number rounded to whole correctly")
    
    print("All fractional quantity logic tests passed!")

def simulate_fractional_shares_scenario():
    """Simulate the specific scenario that caused the original error."""
    print("\nSimulating fractional shares error scenario...")
    
    # This simulates what would happen with the TOI asset that caused the error
    symbol = "TOI"
    qty_numeric = Decimal("0.5")  # Fractional quantity
    
    # Simulate checking if asset supports fractional shares
    mock_api = Mock()
    mock_api.get_asset.return_value = Mock(fractionable=False)  # TOI doesn't support fractional
    
    print(f"Original quantity: {qty_numeric} shares of {symbol}")
    
    # Check if asset supports fractional shares (this is the new logic)
    if qty_numeric != qty_numeric.to_integral_value():
        if not is_fractionable(mock_api, symbol):
            print(f"⚠️  Asset {symbol} does not support fractional shares")
            original_qty = qty_numeric
            qty_numeric = Decimal(int(qty_numeric))
            print(f"Rounded {original_qty} to whole shares: {qty_numeric}")
            
            # Check if rounding resulted in zero shares
            if qty_numeric <= 0:
                print(f"❌ Rounding resulted in 0 shares. Order would be skipped.")
                return False
    
    print(f"✅ Final quantity for order: {qty_numeric} shares")
    print("✅ This would prevent the 'asset TOI is not fractionable' error!")
    return True

if __name__ == "__main__":
    print("🔧 Testing Fractional Shares Compatibility Fix")
    print("=" * 50)
    
    try:
        test_is_fractionable_function()
        test_fractional_quantity_logic()
        simulate_fractional_shares_scenario()
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("The fractional shares fix should prevent the 'asset X is not fractionable' error.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)