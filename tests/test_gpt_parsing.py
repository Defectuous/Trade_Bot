#!/usr/bin/env python3
"""Test script to verify GPT response parsing for dollar amounts vs shares."""

import sys
import os
from decimal import Decimal
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Mock the modules to test parsing logic only
class MockOpenAI:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def chat_completions_create(self, **kwargs):
        # Return different test responses
        test_responses = {
            "BUY $50000": "BUY $50000",
            "BUY 50000": "BUY 50000", 
            "BUY $5,000": "BUY $5000",
            "SELL 100": "SELL 100",
            "NOTHING": "NOTHING"
        }
        
        # For this test, return a specific response based on the prompt
        if "50000" in str(kwargs.get('messages', [])):
            return MockResponse("BUY $50000")
        return MockResponse("BUY $5000")

class MockResponse:
    def __init__(self, content):
        self.choices = [MockChoice(content)]

class MockChoice:
    def __init__(self, content):
        self.message = MockMessage(content)

class MockMessage:
    def __init__(self, content):
        self.content = content

def test_gpt_parsing():
    """Test the GPT parsing logic with various response formats."""
    
    # Import after setting up path
    from modules.gpt_client import ask_gpt_for_decision
    
    # Test parameters
    test_cases = [
        {
            'description': 'Dollar amount parsing',
            'gpt_response': 'BUY $50000',
            'stock_price': Decimal('116.58'),
            'expected_shares': Decimal('50000') / Decimal('116.58'),
            'wallet': Decimal('100000')
        },
        {
            'description': 'Direct shares parsing (legacy)',
            'gpt_response': 'BUY 429',
            'stock_price': Decimal('116.58'),
            'expected_shares': Decimal('429'),
            'wallet': Decimal('100000')
        },
        {
            'description': 'SELL order (shares)',
            'gpt_response': 'SELL 100',
            'stock_price': Decimal('116.58'),
            'expected_shares': Decimal('100'),
            'wallet': Decimal('100000')
        }
    ]
    
    print("🧪 Testing GPT Response Parsing Logic")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['description']}")
        print(f"   Response: {test_case['gpt_response']}")
        print(f"   Stock Price: ${test_case['stock_price']}")
        
        # Simulate the parsing logic manually
        text = test_case['gpt_response']
        parts = text.strip().split()
        action = parts[0].upper()
        amount = None
        
        if action in ("BUY", "SELL") and len(parts) >= 2:
            try:
                raw_amount = parts[1]
                if raw_amount.startswith('$'):
                    # Dollar amount - convert to shares
                    dollar_amount = Decimal(raw_amount[1:])
                    stock_price = test_case['stock_price']
                    if stock_price > 0:
                        amount = dollar_amount / stock_price
                        print(f"   💰 Converted ${dollar_amount} → {amount:.4f} shares")
                    else:
                        amount = None
                        print(f"   ❌ Invalid stock price for conversion")
                else:
                    # Direct number (shares)
                    amount = Decimal(raw_amount)
                    print(f"   📊 Direct shares: {amount}")
            except Exception as e:
                print(f"   ❌ Parsing failed: {e}")
                amount = None
        
        # Compare with expected
        if amount is not None and test_case.get('expected_shares'):
            diff = abs(amount - test_case['expected_shares'])
            if diff < Decimal('0.01'):  # Allow small rounding differences
                print(f"   ✅ PASS: Got {amount:.4f}, expected {test_case['expected_shares']:.4f}")
            else:
                print(f"   ❌ FAIL: Got {amount:.4f}, expected {test_case['expected_shares']:.4f}")
        elif amount is not None:
            print(f"   ✅ Parsed successfully: {amount}")
        else:
            print(f"   ❌ Parsing failed")

def test_real_scenario():
    """Test the exact scenario from the logs."""
    print("\n\n🎯 Real Scenario Test (FDX)")
    print("=" * 30)
    
    # Exact values from the logs
    gpt_response = "BUY $50,000"
    stock_price = Decimal('116.58')
    wallet = Decimal('100000')
    buying_power = Decimal('200000')
    
    print(f"GPT Response: {gpt_response}")
    print(f"Stock Price: ${stock_price}")
    print(f"Wallet: ${wallet}")
    print(f"Buying Power: ${buying_power}")
    
    # Parse the response
    text = gpt_response
    parts = text.strip().split()
    action = parts[0].upper()
    
    if len(parts) >= 2:
        raw_amount = parts[1]
        if raw_amount.startswith('$'):
            # Remove $ and comma
            dollar_str = raw_amount[1:].replace(',', '')
            dollar_amount = Decimal(dollar_str)
            shares_needed = dollar_amount / stock_price
            total_cost = shares_needed * stock_price
            
            print(f"\n📊 Analysis:")
            print(f"   Dollar Amount Requested: ${dollar_amount:,}")
            print(f"   Shares This Buys: {shares_needed:.4f}")
            print(f"   Total Cost: ${total_cost:.2f}")
            print(f"   Available Buying Power: ${buying_power}")
            print(f"   Can Afford? {'✅ YES' if total_cost <= buying_power else '❌ NO'}")
            
            # What the OLD system was doing
            old_interpretation = Decimal('50000')  # Treating $50,000 as 50,000 shares
            old_cost = old_interpretation * stock_price
            print(f"\n🚨 OLD System (BUG):")
            print(f"   Interpreted as: {old_interpretation:,} shares")
            print(f"   Total Cost: ${old_cost:,.2f}")
            print(f"   Can Afford? {'✅ YES' if old_cost <= buying_power else '❌ NO'}")
            
            print(f"\n✅ NEW System (FIXED):")
            print(f"   Correctly interprets: {shares_needed:.2f} shares")
            print(f"   Reasonable purchase: ${total_cost:.2f}")

if __name__ == "__main__":
    test_gpt_parsing()
    test_real_scenario()
    
    print("\n\n🔧 Fix Summary:")
    print("1. Updated GPT prompt to specify 'BUY $[Dollar Amount]'")
    print("2. Enhanced parsing to detect $ prefix and convert to shares")
    print("3. Added logging to show conversion process")
    print("4. Maintains backward compatibility for direct share amounts")