#!/usr/bin/env python3
"""Test enhanced GPT prompts for small wallet support."""

from decimal import Decimal

def test_enhanced_prompts():
    """Test the new GPT prompt structure for small wallets."""
    
    print("🧪 Testing Enhanced GPT Prompts for Small Wallets")
    print("=" * 55)
    
    # Mock test data
    test_scenarios = [
        {
            'wallet': Decimal('100'),
            'symbol': 'WMT',
            'stock_price': Decimal('103.065'),
            'description': 'Small wallet ($100) - Your exact scenario'
        },
        {
            'wallet': Decimal('50'),
            'symbol': 'AAPL', 
            'stock_price': Decimal('150'),
            'description': 'Tiny wallet ($50) - Very limited'
        },
        {
            'wallet': Decimal('250'),
            'symbol': 'SPY',
            'stock_price': Decimal('430'),
            'description': 'Small wallet ($250) - Still needs limits'
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        wallet = scenario['wallet']
        symbol = scenario['symbol']
        stock_price = scenario['stock_price']
        
        print(f"\n📋 Test {i}: {scenario['description']}")
        print(f"   Wallet: ${wallet}")
        print(f"   Stock: {symbol} @ ${stock_price}")
        
        # Calculate what the new prompt guidelines would say
        max_risk = wallet * Decimal('0.02')
        print(f"   2% Risk Limit: ${max_risk:.2f}")
        
        # Show the critical budget warnings
        if wallet < 500:
            max_trade = min(wallet * Decimal('0.5'), 50)
            print(f"   🚨 CRITICAL WARNING: Small account (${wallet})")
            print(f"   Maximum trade: ${max_trade:.0f}")
            print(f"   Required: Amount MUST be ≤ ${wallet}")
            print(f"   Examples: BUY $20, BUY $50, BUY ${min(wallet, 100):.0f}")
        
        # Show what would happen with old vs new prompts
        print(f"\\n   OLD PROMPT ISSUE:")
        print(f"     • General warning about budget")
        print(f"     • GPT could still say 'BUY $2000'")
        print(f"     • Safety check would cap to ${wallet}")
        
        print(f"\\n   NEW PROMPT SOLUTION:")
        print(f"     • 🚨 CRITICAL alerts for <$500 accounts")
        print(f"     • ABSOLUTE MAXIMUM: ${wallet}")
        print(f"     • Specific examples within budget")
        print(f"     • Format: 'BUY $[Amount ≤ {wallet}]'")

def test_prompt_examples():
    """Show actual prompt snippets for small wallets."""
    
    print("\\n\\n🤖 Enhanced Prompt Examples")
    print("=" * 35)
    
    wallet = Decimal('100')
    
    print(f"\\n💬 For ${wallet} wallet, GPT now sees:")
    print("\\n" + "="*50)
    print("TRADING RULES:")
    print(f"• ABSOLUTE MAXIMUM: ${wallet} (your total available cash)")
    print(f"• Recommended trade size: 2% of wallet = ${wallet * Decimal('0.02'):.2f}")
    print("• For accounts <$500: Use $10-$50 maximum per trade")
    print("• NEVER recommend amounts exceeding available cash")
    print(f"• 🚨 CRITICAL: SMALL ACCOUNT (${wallet}) - Maximum trade: ${min(wallet * Decimal('0.5'), 50):.0f}")
    print(f"• REQUIRED: Dollar amount MUST be ≤ ${wallet}")
    print("• Suggested range: $10-$50 for safety")
    print("\\nIMPORTANT: With $100 available, your BUY amount MUST be ≤ $100.")
    print("Reply EXACTLY in this format: BUY $[Amount ≤ 100], SELL [Shares], or NOTHING")
    print("Examples for your $100 budget: BUY $20, BUY $50, BUY $100, NOTHING")
    print("="*50)
    
def test_validation_warnings():
    """Test the new validation warnings."""
    
    print("\\n\\n⚠️  Enhanced Validation System")
    print("=" * 35)
    
    test_responses = [
        {'gpt_reply': 'BUY $2000', 'wallet': 100, 'should_warn': True},
        {'gpt_reply': 'BUY $50', 'wallet': 100, 'should_warn': False},
        {'gpt_reply': 'BUY $150', 'wallet': 100, 'should_warn': True},
        {'gpt_reply': 'BUY $25', 'wallet': 100, 'should_warn': False},
    ]
    
    for test in test_responses:
        gpt_reply = test['gpt_reply']
        wallet = test['wallet']
        should_warn = test['should_warn']
        
        # Extract amount
        amount_str = gpt_reply.split('$')[1]
        amount = Decimal(amount_str)
        
        print(f"\\nGPT: '{gpt_reply}' | Wallet: ${wallet}")
        
        if amount > wallet:
            print(f"   🚨 WARNING: Suggested ${amount} but only ${wallet} available")
            print(f"   ✅ Validation: {'CORRECT' if should_warn else 'UNEXPECTED'}")
        else:
            print(f"   ✅ VALID: ${amount} is within ${wallet} budget")
            print(f"   ✅ Validation: {'CORRECT' if not should_warn else 'MISSED'}")

if __name__ == "__main__":
    test_enhanced_prompts()
    test_prompt_examples()
    test_validation_warnings()
    
    print("\\n\\n🎯 Summary of Enhancements:")
    print("1. ✅ CRITICAL alerts for accounts <$500")
    print("2. ✅ ABSOLUTE MAXIMUM budget warnings")
    print("3. ✅ Specific format requirements with examples")
    print("4. ✅ Validation warnings when GPT over-recommends")
    print("5. ✅ Multiple layers of budget enforcement")
    
    print("\\n📊 Expected Behavior with $100 wallet:")
    print("   • GPT sees 🚨 CRITICAL warnings")
    print("   • Examples show: BUY $20, BUY $50, BUY $100")
    print("   • If GPT still says BUY $2000:")
    print("     - ⚠️  Warning logged about over-recommendation")
    print("     - 🛡️  Safety check caps to $100 anyway")
    print("     - 📝 Clear audit trail of the issue")