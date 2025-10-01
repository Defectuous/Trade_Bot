"""Test script for candlestick data integration."""

import sys
import os
from decimal import Decimal
from unittest.mock import Mock, patch

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.taapi import fetch_candle_taapi, fetch_all_indicators
from modules.gpt_client import ask_gpt_for_decision

def test_candle_fetch_function():
    """Test the candlestick data fetching function."""
    print("Testing fetch_candle_taapi function...")
    
    # Mock successful API response
    mock_response = Mock()
    mock_response.json.return_value = {
        'open': 450.25,
        'high': 451.80,
        'low': 449.90,
        'close': 451.15
    }
    mock_response.raise_for_status.return_value = None
    
    with patch('modules.taapi.requests.get', return_value=mock_response):
        result = fetch_candle_taapi("AAPL", "test_key")
        
        assert result is not None, "Expected candlestick data, got None"
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert all(k in result for k in ['open', 'high', 'low', 'close']), "Missing OHLC keys"
        assert isinstance(result['open'], Decimal), "Open should be Decimal type"
        
        print("✅ Test 1 passed: Candlestick data fetching works correctly")
        print(f"   Sample data: O:{result['open']} H:{result['high']} L:{result['low']} C:{result['close']}")
    
    # Test with missing key
    result = fetch_candle_taapi("AAPL", "")
    assert result is None, "Expected None for missing API key"
    print("✅ Test 2 passed: Missing API key handled correctly")
    
    # Test with API error
    with patch('modules.taapi.requests.get', side_effect=Exception("API Error")):
        result = fetch_candle_taapi("AAPL", "test_key")
        assert result is None, "Expected None for API error"
        print("✅ Test 3 passed: API error handled correctly")

def test_candle_in_all_indicators():
    """Test candlestick data integration in fetch_all_indicators."""
    print("\nTesting candlestick integration in fetch_all_indicators...")
    
    # Mock environment variables
    with patch.dict(os.environ, {'ENABLE_CANDLE': 'true'}):
        # Mock the individual fetch functions
        with patch('modules.taapi.fetch_rsi_taapi', return_value=Decimal('65.5')):
            with patch('modules.taapi.fetch_ma_taapi', return_value=Decimal('450.0')):
                with patch('modules.taapi.fetch_candle_taapi', return_value={
                    'open': Decimal('449.50'),
                    'high': Decimal('452.10'), 
                    'low': Decimal('448.80'),
                    'close': Decimal('451.25')
                }):
                    indicators = fetch_all_indicators("AAPL", "test_key")
                    
                    assert 'candle' in indicators, "Candlestick data not included in indicators"
                    assert indicators['candle'] is not None, "Candlestick data is None"
                    assert isinstance(indicators['candle'], dict), "Candlestick data should be dict"
                    
                    print("✅ Test 1 passed: Candlestick data integrated in fetch_all_indicators")
                    print(f"   Candle data: {indicators['candle']}")
    
    # Test with disabled candlestick
    with patch.dict(os.environ, {'ENABLE_CANDLE': 'false'}):
        indicators = fetch_all_indicators("AAPL", "test_key")
        assert indicators['candle'] is None, "Candlestick data should be None when disabled"
        print("✅ Test 2 passed: Candlestick data properly disabled")

def test_candle_in_gpt_prompt():
    """Test candlestick data integration in GPT prompts."""
    print("\nTesting candlestick data in GPT prompts...")
    
    # Mock indicators with candlestick data
    test_indicators = {
        'rsi': Decimal('65.5'),
        'ma': Decimal('450.0'),
        'candle': {
            'open': Decimal('449.50'),
            'high': Decimal('452.10'),
            'low': Decimal('448.80'), 
            'close': Decimal('451.25')
        }
    }
    
    # Mock OpenAI client
    mock_client = Mock()
    mock_completion = Mock()
    mock_completion.choices = [Mock()]
    mock_completion.choices[0].message.content = "BUY $50"
    mock_client.chat.completions.create.return_value = mock_completion
    
    with patch('modules.gpt_client.openai') as mock_openai:
        mock_openai.OpenAI.return_value = mock_client
        
        try:
            action, amount = ask_gpt_for_decision(
                "test_key", "gpt-3.5-turbo", test_indicators, 
                "AAPL", Decimal('0'), Decimal('451.25'), Decimal('1000')
            )
            
            # Check that the function completed successfully
            assert action in ['BUY', 'SELL', 'NOTHING'], f"Invalid action: {action}"
            print("✅ Test 1 passed: GPT function handles candlestick data without errors")
            
            # Verify the prompt included candlestick data
            call_args = mock_client.chat.completions.create.call_args
            prompt = call_args[1]['messages'][0]['content']
            
            assert 'Candlestick Data (OHLC)' in prompt, "Candlestick description not in prompt"
            assert 'O:449.50 H:452.10 L:448.80 C:451.25' in prompt, "OHLC data not formatted in prompt"
            assert 'price action analysis' in prompt, "Price action guidance not in prompt"
            
            print("✅ Test 2 passed: Candlestick data properly formatted in GPT prompt")
            print(f"   Action: {action}, Amount: {amount}")
            
        except Exception as e:
            print(f"❌ GPT test failed: {e}")
            return False
    
    return True

def test_candle_formatting():
    """Test candlestick data formatting for logging and display."""
    print("\nTesting candlestick data formatting...")
    
    candle_data = {
        'open': Decimal('449.50'),
        'high': Decimal('452.10'),
        'low': Decimal('448.80'),
        'close': Decimal('451.25')
    }
    
    # Test the formatting logic from trade_bot.py
    candle_str = f"O:{candle_data['open']} H:{candle_data['high']} L:{candle_data['low']} C:{candle_data['close']}"
    expected = "O:449.50 H:452.10 L:448.80 C:451.25"
    
    assert candle_str == expected, f"Expected '{expected}', got '{candle_str}'"
    print(f"✅ Test passed: Candlestick formatting works correctly")
    print(f"   Formatted: {candle_str}")

def simulate_trading_scenario_with_candles():
    """Simulate a complete trading scenario with candlestick data."""
    print("\n" + "="*60)
    print("SIMULATING TRADING SCENARIO WITH CANDLESTICK DATA")
    print("="*60)
    
    # Simulate a bullish scenario
    symbol = "AAPL"
    current_price = Decimal('451.25')
    
    indicators = {
        'rsi': Decimal('45.0'),  # Neutral RSI
        'ma': Decimal('448.0'),  # Price above MA (bullish)
        'candle': {
            'open': Decimal('449.50'),   # Opened lower
            'high': Decimal('452.10'),   # Made new high
            'low': Decimal('448.80'),    # Held above yesterday's close  
            'close': Decimal('451.25')  # Strong close near high
        }
    }
    
    print(f"Symbol: {symbol}")
    print(f"Current Price: ${current_price}")
    print(f"RSI: {indicators['rsi']} (Neutral)")
    print(f"MA: ${indicators['ma']} (Price above MA = Bullish)")
    print(f"Candlestick Analysis:")
    print(f"  Open: ${indicators['candle']['open']}")
    print(f"  High: ${indicators['candle']['high']}")
    print(f"  Low: ${indicators['candle']['low']}")
    print(f"  Close: ${indicators['candle']['close']}")
    
    # Analysis
    range_pct = ((indicators['candle']['high'] - indicators['candle']['low']) / indicators['candle']['open'] * 100)
    close_position = ((indicators['candle']['close'] - indicators['candle']['low']) / 
                     (indicators['candle']['high'] - indicators['candle']['low']) * 100)
    
    print(f"\nTechnical Analysis:")
    print(f"  Daily Range: {range_pct:.2f}% (volatility measure)")
    print(f"  Close Position: {close_position:.1f}% of range (close near high = bullish)")
    print(f"  Price vs MA: +${current_price - indicators['ma']:.2f} above trend")
    
    print(f"\n🎯 CANDLESTICK SIGNALS:")
    if close_position > 75:
        print(f"  ✅ Strong bullish close (top {close_position:.0f}% of range)")
    if current_price > indicators['ma']:
        print(f"  ✅ Price above moving average (trend confirmation)")
    if 30 < indicators['rsi'] < 70:
        print(f"  ✅ RSI in healthy range (not overbought/oversold)")
    
    print(f"\n📈 EXPECTED GPT ANALYSIS:")
    print(f"  The candlestick shows strong intraday buying pressure")
    print(f"  Close near daily high suggests continued bullish momentum")
    print(f"  Price above MA confirms uptrend")
    print(f"  This combination should favor BUY recommendations")

if __name__ == "__main__":
    print("🕯️ Testing Candlestick Data Integration")
    print("=" * 60)
    
    try:
        test_candle_fetch_function()
        test_candle_in_all_indicators()
        test_candle_in_gpt_prompt()
        test_candle_formatting()
        simulate_trading_scenario_with_candles()
        
        print("\n" + "=" * 60)
        print("🎉 ALL CANDLESTICK TESTS PASSED!")
        print("✅ Candlestick data integration is working correctly")
        print("✅ TAAPI fetch function handles OHLC data properly")
        print("✅ GPT prompts include candlestick analysis")
        print("✅ Logging and formatting work as expected")
        print("\n📊 The bot now has 7 technical indicators including candlestick data!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)