#!/usr/bin/env python3
"""Test comma handling in GPT parsing."""

from decimal import Decimal

def test_comma_handling():
    """Test comma handling in dollar amounts."""
    test_cases = ['$50,000', '$5000', '50,000', '5000']
    print('Testing comma handling:')
    
    for test in test_cases:
        try:
            if test.startswith('$'):
                cleaned = test[1:].replace(',', '')
                amount = Decimal(cleaned)
                print(f'{test} -> ${amount}')
            else:
                cleaned = test.replace(',', '')
                amount = Decimal(cleaned)
                print(f'{test} -> {amount} shares')
        except Exception as e:
            print(f'{test} -> ERROR: {e}')
    
    # Test the exact scenario from logs
    print('\n' + '='*40)
    print('Real scenario test:')
    
    gpt_response = 'BUY $50,000'
    stock_price = Decimal('116.58')
    parts = gpt_response.split()
    raw_amount = parts[1]
    
    print(f'GPT Response: {gpt_response}')
    print(f'Raw amount: {raw_amount}')
    
    if raw_amount.startswith('$'):
        dollar_str = raw_amount[1:].replace(',', '')
        dollar_amount = Decimal(dollar_str)
        shares = dollar_amount / stock_price
        total_cost = shares * stock_price
        
        print(f'Dollar string after cleanup: "{dollar_str}"')
        print(f'Dollar amount: ${dollar_amount}')
        print(f'Stock price: ${stock_price}')
        print(f'Shares to buy: {shares:.4f}')
        print(f'Total cost: ${total_cost:.2f}')
        
        # Compare to old bug
        old_shares = Decimal('50000')  # What it was interpreting before
        old_cost = old_shares * stock_price
        print(f'\nOLD BUG would have tried:')
        print(f'Shares: {old_shares:,}')
        print(f'Cost: ${old_cost:,.2f}')
        
        print(f'\nFIX correctly does:')
        print(f'Shares: {shares:.2f}')
        print(f'Cost: ${total_cost:,.2f}')

if __name__ == "__main__":
    test_comma_handling()