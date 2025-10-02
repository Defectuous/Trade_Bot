#!/usr/bin/env python3
"""
Quick test of configured symbols from .env
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
from modules.taapi import fetch_rsi_taapi, fetch_all_indicators

load_dotenv()
taapi_key = os.environ.get('TAAPI_KEY')

# Get configured symbols
symbols_env = os.environ.get("SYMBOLS")
if symbols_env:
    symbols = [s.strip().upper() for s in symbols_env.split(",") if s.strip()]
else:
    symbols = [os.environ.get("SYMBOL", "AAPL").upper()]

print(f"Testing configured symbols: {', '.join(symbols)}")
print("=" * 50)

for symbol in symbols:
    print(f"\n📈 {symbol}:")
    try:
        # Test RSI first
        rsi = fetch_rsi_taapi(symbol, taapi_key)
        if rsi:
            print(f"  ✅ RSI: {rsi}")
        else:
            print(f"  ❌ RSI: No data")
            continue
        
        # Test all indicators
        indicators = fetch_all_indicators(symbol, taapi_key)
        if indicators:
            working = 0
            for name, value in indicators.items():
                if value is not None and value != 'N/A':
                    working += 1
                    if name == 'candle' and isinstance(value, dict):
                        print(f"  ✅ {name.upper()}: OHLC data available")
                    else:
                        print(f"  ✅ {name.upper()}: {value}")
                else:
                    print(f"  ❌ {name.upper()}: No data")
            print(f"  📊 Summary: {working}/7 indicators working")
        else:
            print(f"  ❌ fetch_all_indicators failed")
    
    except Exception as e:
        print(f"  ❌ Error: {e}")

print(f"\n✅ Test completed!")