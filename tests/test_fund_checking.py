#!/usr/bin/env python3
"""
Test script for fund checking functionality in the trading bot
"""
import sys
import os
from decimal import Decimal
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.alpaca_client import can_buy, get_wallet_amount

def test_fund_checking():
    """Test various fund checking scenarios"""
    print("🧪 Testing Fund Checking Logic...")
    
    # Mock API client
    mock_api = Mock()
    
    # Test scenarios
    test_cases = [
        {
            "name": "Sufficient funds",
            "buying_power": 1000.00,
            "price": 100.00,
            "qty": 5,
            "expected": True
        },
        {
            "name": "Insufficient funds",
            "buying_power": 100.00,
            "price": 150.00,
            "qty": 1,
            "expected": False
        },
        {
            "name": "Exactly enough (no buffer)",
            "buying_power": 100.00,
            "price": 100.00,
            "qty": 1,
            "expected": False  # Should fail due to 0.5% buffer
        },
        {
            "name": "Fractional shares - sufficient",
            "buying_power": 1000.00,
            "price": 200.00,
            "qty": 0.5,
            "expected": True
        },
        {
            "name": "Fractional shares - insufficient",
            "buying_power": 50.00,
            "price": 200.00,
            "qty": 0.5,
            "expected": False
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {case['name']}")
        print(f"   Buying Power: ${case['buying_power']}")
        print(f"   Price: ${case['price']}")
        print(f"   Quantity: {case['qty']}")
        
        # Mock the get_wallet_amount function
        with patch('modules.alpaca_client.get_wallet_amount') as mock_wallet:
            mock_wallet.return_value = Decimal(str(case['buying_power']))
            
            result = can_buy(mock_api, Decimal(str(case['price'])), case['qty'])
            
            if result == case['expected']:
                print(f"   ✅ PASS: Expected {case['expected']}, got {result}")
            else:
                print(f"   ❌ FAIL: Expected {case['expected']}, got {result}")
    
    print("\n🔍 Edge Case Tests...")
    
    # Test error handling
    with patch('modules.alpaca_client.get_wallet_amount') as mock_wallet:
        mock_wallet.side_effect = Exception("API Error")
        result = can_buy(mock_api, Decimal("100"), 1)
        print(f"   API Error Handling: {result} (should be False)")
    
    print("\n💡 Fund Checking Test Complete!")

if __name__ == "__main__":
    test_fund_checking()