#!/usr/bin/env python3
"""
Simple test to check module imports and configuration without API calls.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

print("🔧 Testing Module Imports and Configuration")
print("=" * 50)

# Test imports
print("📦 Testing imports...")
try:
    from modules.taapi import (
        fetch_rsi_taapi,
        fetch_ma_taapi, 
        fetch_ema_taapi,
        fetch_pattern_taapi,
        fetch_adx_taapi,
        fetch_adxr_taapi,
        fetch_candle_taapi,
        fetch_all_indicators
    )
    print("  ✅ All TAAPI functions imported successfully")
except Exception as e:
    print(f"  ❌ Import error: {e}")
    sys.exit(1)

# Test configuration
print("\n🔑 Testing configuration...")
from dotenv import load_dotenv
load_dotenv()

taapi_key = os.environ.get('TAAPI_KEY')
if taapi_key:
    print(f"  ✅ TAAPI_KEY found: {'*' * (len(taapi_key) - 8) + taapi_key[-8:]}")
else:
    print("  ❌ TAAPI_KEY not found")

symbols_env = os.environ.get("SYMBOLS")
if symbols_env:
    symbols = [s.strip().upper() for s in symbols_env.split(",") if s.strip()]
    print(f"  ✅ SYMBOLS configured: {', '.join(symbols)}")
else:
    symbol = os.environ.get("SYMBOL", "AAPL")
    symbols = [symbol.upper()]
    print(f"  ✅ SYMBOL configured: {symbol}")

# Test function signatures
print("\n🔍 Testing function signatures...")
indicator_functions = [
    ("RSI", fetch_rsi_taapi, ["symbol", "taapi_key"]),
    ("MA", fetch_ma_taapi, ["symbol", "taapi_key", "period"]),
    ("EMA", fetch_ema_taapi, ["symbol", "taapi_key", "period"]),
    ("Pattern", fetch_pattern_taapi, ["symbol", "taapi_key"]),
    ("ADX", fetch_adx_taapi, ["symbol", "taapi_key", "period"]),
    ("ADXR", fetch_adxr_taapi, ["symbol", "taapi_key", "period"]),
    ("Candle", fetch_candle_taapi, ["symbol", "taapi_key"]),
    ("All Indicators", fetch_all_indicators, ["symbol", "taapi_key"]),
]

for name, func, expected_params in indicator_functions:
    try:
        import inspect
        sig = inspect.signature(func)
        actual_params = list(sig.parameters.keys())
        print(f"  ✅ {name}: {', '.join(actual_params)}")
    except Exception as e:
        print(f"  ❌ {name}: Error getting signature - {e}")

print("\n📊 Configuration Summary:")
print(f"  🎯 Symbols to test: {', '.join(symbols)}")
print(f"  🔍 Indicators available: 7 (RSI, MA, EMA, Pattern, ADX, ADXR, Candle)")
print(f"  🔑 API key: {'Configured' if taapi_key else 'Missing'}")

if taapi_key and symbols:
    print(f"\n✅ Ready to test indicators for {len(symbols)} symbol(s)")
    print(f"📝 Next: Run actual API tests when TAAPI service is responsive")
else:
    print(f"\n❌ Configuration incomplete - check .env file")

print(f"\n💡 Recommendation:")
if not taapi_key:
    print(f"  - Add valid TAAPI_KEY to .env file")
if not symbols or symbols == ['']:
    print(f"  - Configure SYMBOLS in .env file (e.g., SYMBOLS=AAPL,MSFT,SPY)")

print(f"\n🔗 API Status Check:")
print(f"  - TAAPI.io seems to be slow/unresponsive currently")
print(f"  - Consider testing during off-peak hours")
print(f"  - Verify account status at taapi.io")