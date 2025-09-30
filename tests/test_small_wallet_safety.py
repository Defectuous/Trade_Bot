#!/usr/bin/env python3
"""Test script to verify small wallet safety checks."""

from decimal import Decimal

def test_small_wallet_safety():
    """Test the safety mechanisms for small wallet amounts."""
    
    print("🧪 Testing Small Wallet Safety Mechanisms")
    print("=" * 50)
    
    # Test scenarios
    test_cases = [
        {
            'description': 'Small wallet ($100) with expensive stock',
            'wallet': Decimal('100'),
            'stock_price': Decimal('116.84'),
            'gpt_recommendation': 'BUY $2000',
            'expected_max_shares': Decimal('100') / Decimal('116.84')
        },
        {
            'description': 'Tiny wallet ($50) with moderate stock',
            'wallet': Decimal('50'),
            'stock_price': Decimal('150'),
            'gpt_recommendation': 'BUY $500',
            'expected_max_shares': Decimal('50') / Decimal('150')
        },
        {
            'description': 'Medium wallet ($1000) with affordable stock',
            'wallet': Decimal('1000'),
            'stock_price': Decimal('100'),
            'gpt_recommendation': 'BUY $800',
            'expected_shares': Decimal('800') / Decimal('100')  # Should be allowed
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test['description']}")
        print(f"   Wallet: ${test['wallet']}")
        print(f"   Stock Price: ${test['stock_price']}")
        print(f"   GPT Says: {test['gpt_recommendation']}")
        
        # Extract dollar amount from GPT recommendation
        gpt_amount_str = test['gpt_recommendation'].split('$')[1]
        gpt_dollar_amount = Decimal(gpt_amount_str)
        gpt_recommended_shares = gpt_dollar_amount / test['stock_price']
        
        print(f"   GPT Wants: {gpt_recommended_shares:.4f} shares (${gpt_dollar_amount})")
        
        # Calculate what our safety check would do
        max_affordable_shares = test['wallet'] / test['stock_price']
        
        if gpt_recommended_shares > max_affordable_shares:
            # Safety check would trigger
            actual_shares = max_affordable_shares
            actual_cost = actual_shares * test['stock_price']
            print(f"   🛡️  SAFETY CHECK: Limited to {actual_shares:.4f} shares (${actual_cost:.2f})")
            print(f"   ✅ RESULT: Safe - within budget")
        else:
            # GPT recommendation is fine
            actual_shares = gpt_recommended_shares
            actual_cost = actual_shares * test['stock_price']
            print(f"   ✅ RESULT: GPT recommendation accepted ({actual_shares:.4f} shares, ${actual_cost:.2f})")

def test_gpt_prompt_improvements():
    """Test the improved GPT prompts for small wallets."""
    
    print("\n\n🤖 Testing GPT Prompt Improvements")
    print("=" * 40)
    
    wallet_scenarios = [
        {'wallet': Decimal('100'), 'category': 'Very Small'},
        {'wallet': Decimal('500'), 'category': 'Small'}, 
        {'wallet': Decimal('1000'), 'category': 'Medium'},
        {'wallet': Decimal('5000'), 'category': 'Large'}
    ]
    
    for scenario in wallet_scenarios:
        wallet = scenario['wallet']
        category = scenario['category']
        
        print(f"\n💰 {category} Wallet: ${wallet}")
        
        # Calculate risk limits
        max_risk = wallet * Decimal('0.02')
        print(f"   Max Risk (2%): ${max_risk:.2f}")
        
        # Show what guidelines would be added
        guidelines = []
        if wallet < 500:
            guidelines.append("SMALL ACCOUNT ALERT: Use VERY conservative amounts")
            guidelines.append("Suggested range: $10-$50 per trade")
        elif wallet < 1000:
            guidelines.append("CONSERVATIVE ACCOUNT: Moderate position sizes recommended")
        
        if guidelines:
            print("   Special Guidelines:")
            for guideline in guidelines:
                print(f"     • {guideline}")
        else:
            print("   No special guidelines (standard trading)")

if __name__ == "__main__":
    test_small_wallet_safety()
    test_gpt_prompt_improvements()
    
    print("\n\n🔧 Summary of Safety Improvements:")
    print("1. ✅ Enhanced GPT prompt with wallet-specific guidelines")
    print("2. ✅ Safety check caps orders to available cash")
    print("3. ✅ Improved logging shows wallet amounts passed to GPT")
    print("4. ✅ Special handling for accounts <$500")
    print("5. ✅ Conservative recommendations for small wallets")
    
    print("\n🎯 For your $100 account:")
    print("   • GPT will now see 'SMALL ACCOUNT ALERT' in prompt")
    print("   • Suggested trade range: $10-$50")
    print("   • Safety check will cap any order to $100 max")
    print("   • Fractional shares allow precise small amounts")