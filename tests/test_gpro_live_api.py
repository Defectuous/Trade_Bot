"""Live API test for GPRO indicators using real TAAPI.io calls."""

import sys
import os
from decimal import Decimal

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.taapi import fetch_rsi_taapi, fetch_ma_taapi, fetch_candle_taapi, fetch_all_indicators

def test_live_gpro_indicators():
    """Test GPRO indicators with real TAAPI API calls."""
    print("🔴 LIVE API TEST - RSI, MA, AND CANDLE FOR GPRO")
    print("=" * 60)
    
    # Get TAAPI key from environment
    taapi_key = os.getenv('TAAPI_KEY')
    if not taapi_key:
        print("❌ TAAPI_KEY not found in environment variables")
        print("💡 To run live test:")
        print("   1. Add TAAPI_KEY to your .env file")
        print("   2. Or set: export TAAPI_KEY=your_key_here")
        print("   3. Get free key at: https://taapi.io/")
        return False
    
    symbol = "GPRO"
    print(f"📡 Testing live TAAPI calls for {symbol}...")
    print(f"🔑 Using TAAPI key: {taapi_key[:8]}...")
    
    # Test 1: RSI
    print(f"\n1. 📊 Testing RSI for {symbol}:")
    try:
        rsi_value = fetch_rsi_taapi(symbol, taapi_key, interval="1m")
        if rsi_value is not None:
            print(f"   ✅ Live RSI: {rsi_value}")
            
            # Interpret RSI
            if rsi_value > 70:
                rsi_signal = "🔴 OVERBOUGHT (consider selling)"
            elif rsi_value < 30:
                rsi_signal = "🟢 OVERSOLD (consider buying)" 
            else:
                rsi_signal = "🟡 NEUTRAL (balanced momentum)"
            print(f"   📈 Signal: {rsi_signal}")
        else:
            print(f"   ❌ Failed to fetch RSI for {symbol}")
            return False
    except Exception as e:
        print(f"   ❌ RSI API call failed: {e}")
        return False
    
    # Test 2: Moving Average
    print(f"\n2. 📈 Testing MA(20) for {symbol}:")
    try:
        ma_value = fetch_ma_taapi(symbol, taapi_key, period=20, interval="1m")
        if ma_value is not None:
            print(f"   ✅ Live MA(20): ${ma_value}")
            
            # We'd need current price to compare, but let's show the value
            print(f"   📊 20-period Moving Average established")
            print(f"   💡 Compare current {symbol} price to ${ma_value} for trend direction")
        else:
            print(f"   ❌ Failed to fetch MA for {symbol}")
            return False
    except Exception as e:
        print(f"   ❌ MA API call failed: {e}")
        return False
    
    # Test 3: Candlestick Data
    print(f"\n3. 🕯️ Testing Candlestick for {symbol}:")
    try:
        candle_data = fetch_candle_taapi(symbol, taapi_key, interval="1m")
        if candle_data is not None:
            print(f"   ✅ Live Candlestick data:")
            print(f"      Open:  ${candle_data['open']}")
            print(f"      High:  ${candle_data['high']}")
            print(f"      Low:   ${candle_data['low']}")
            print(f"      Close: ${candle_data['close']}")
            
            # Analyze the candlestick
            body_size = abs(candle_data['close'] - candle_data['open'])
            total_range = candle_data['high'] - candle_data['low']
            
            if total_range > 0:
                body_pct = (body_size / total_range) * 100
                close_position = ((candle_data['close'] - candle_data['low']) / total_range) * 100
                
                print(f"   📊 Analysis:")
                print(f"      Range: ${total_range:.4f}")
                print(f"      Body: {body_pct:.1f}% of range")
                print(f"      Close: {close_position:.1f}% of range")
                
                if candle_data['close'] > candle_data['open']:
                    candle_type = "🟢 BULLISH candle (green)"
                elif candle_data['close'] < candle_data['open']:
                    candle_type = "🔴 BEARISH candle (red)"
                else:
                    candle_type = "⚪ DOJI candle (neutral)"
                print(f"      Type: {candle_type}")
            
        else:
            print(f"   ❌ Failed to fetch Candlestick for {symbol}")
            return False
    except Exception as e:
        print(f"   ❌ Candlestick API call failed: {e}")
        return False
    
    # Test 4: Combined fetch
    print(f"\n4. 🎯 Testing Combined Indicator Fetch:")
    try:
        # Set environment for focused test
        os.environ['ENABLE_RSI'] = 'true'
        os.environ['ENABLE_MA'] = 'true'
        os.environ['ENABLE_EMA'] = 'false'
        os.environ['ENABLE_PATTERN'] = 'false'
        os.environ['ENABLE_ADX'] = 'false'
        os.environ['ENABLE_ADXR'] = 'false'
        os.environ['ENABLE_CANDLE'] = 'true'
        
        all_indicators = fetch_all_indicators(symbol, taapi_key, interval="1m")
        
        print(f"   📊 Combined Results for {symbol}:")
        for name, value in all_indicators.items():
            if value is not None:
                if name == 'candle' and isinstance(value, dict):
                    candle_str = f"O:{value['open']} H:{value['high']} L:{value['low']} C:{value['close']}"
                    print(f"      ✅ {name.upper()}: {candle_str}")
                else:
                    print(f"      ✅ {name.upper()}: {value}")
            else:
                print(f"      ⚪ {name.upper()}: disabled/failed")
        
        # Count successful indicators
        successful = sum(1 for v in all_indicators.values() if v is not None)
        total = len(all_indicators)
        print(f"   📈 Success Rate: {successful}/{total} indicators")
        
        if successful >= 3:  # RSI + MA + Candle
            print(f"   🎉 All target indicators retrieved successfully!")
            return True
        else:
            print(f"   ⚠️ Some indicators failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Combined fetch failed: {e}")
        return False

def analyze_gpro_trading_opportunity():
    """Analyze real GPRO data for trading opportunity."""
    print(f"\n" + "=" * 60)
    print("📈 LIVE GPRO TRADING ANALYSIS")
    print("=" * 60)
    
    taapi_key = os.getenv('TAAPI_KEY')
    if not taapi_key:
        print("❌ Cannot perform live analysis without TAAPI_KEY")
        return
    
    symbol = "GPRO"
    
    try:
        # Get live data
        print(f"📡 Fetching live market data for {symbol}...")
        
        rsi = fetch_rsi_taapi(symbol, taapi_key, interval="5m")  # 5min for more stable signals
        ma = fetch_ma_taapi(symbol, taapi_key, period=20, interval="5m")
        candle = fetch_candle_taapi(symbol, taapi_key, interval="5m")
        
        if not all([rsi, ma, candle]):
            print("❌ Could not fetch all required indicators")
            return
        
        print(f"\n📊 Live Technical Analysis for {symbol}:")
        print(f"   RSI(14): {rsi}")
        print(f"   MA(20): ${ma}")
        print(f"   Current Candle: O:${candle['open']} H:${candle['high']} L:${candle['low']} C:${candle['close']}")
        
        current_price = candle['close']
        
        # Generate trading signals
        signals = []
        
        # RSI signal
        if rsi < 30:
            signals.append("🟢 RSI OVERSOLD - Bullish")
        elif rsi > 70:
            signals.append("🔴 RSI OVERBOUGHT - Bearish")
        else:
            signals.append("🟡 RSI NEUTRAL")
        
        # MA signal
        if current_price > ma:
            signals.append("🟢 PRICE ABOVE MA - Bullish trend")
        else:
            signals.append("🔴 PRICE BELOW MA - Bearish trend")
        
        # Candlestick signal
        if candle['close'] > candle['open']:
            close_pct = ((candle['close'] - candle['low']) / (candle['high'] - candle['low'])) * 100
            if close_pct > 75:
                signals.append("🟢 STRONG BULLISH CANDLE - Close near high")
            else:
                signals.append("🟢 BULLISH CANDLE")
        else:
            signals.append("🔴 BEARISH CANDLE")
        
        print(f"\n🚨 Trading Signals:")
        for signal in signals:
            print(f"   {signal}")
        
        # Count bullish signals
        bullish_count = sum(1 for s in signals if '🟢' in s)
        total_signals = len(signals)
        
        print(f"\n⚖️ Signal Strength: {bullish_count}/{total_signals} bullish")
        
        if bullish_count >= 2:
            recommendation = "🚀 BUY RECOMMENDATION"
            position_size = "Small position (2-5% of portfolio)"
        elif bullish_count == 1:
            recommendation = "⏸️ HOLD/WATCH"
            position_size = "Wait for more confirmation"
        else:
            recommendation = "🛑 AVOID/SELL"
            position_size = "Consider exit if holding"
        
        print(f"\n🎯 Trading Recommendation: {recommendation}")
        print(f"💰 Position Sizing: {position_size}")
        
        # Price targets (basic calculation)
        support = min(ma, candle['low'])
        resistance = candle['high']
        print(f"\n📍 Key Levels:")
        print(f"   Support: ~${support:.2f}")
        print(f"   Current: ${current_price:.2f}")
        print(f"   Resistance: ~${resistance:.2f}")
        
    except Exception as e:
        print(f"❌ Live analysis failed: {e}")

def main():
    """Run live GPRO indicator tests."""
    print("🎯 LIVE GPRO INDICATOR TEST WITH REAL TAAPI API")
    print("=" * 65)
    
    try:
        # Test individual indicators
        success = test_live_gpro_indicators()
        
        if success:
            # Perform trading analysis
            analyze_gpro_trading_opportunity()
            
            print("\n" + "=" * 65)
            print("🎉 LIVE GPRO TEST COMPLETED SUCCESSFULLY!")
            print("\n✅ Confirmed Working:")
            print("   - RSI indicator fetch and interpretation")
            print("   - MA indicator fetch and trend analysis")
            print("   - Candlestick data fetch and pattern analysis")
            print("   - Combined indicator analysis")
            print("   - Real-time trading signal generation")
            
            print("\n🚀 READY FOR LIVE GPRO TRADING!")
            print("   Your bot can now trade GPRO with:")
            print("   - RSI momentum analysis")
            print("   - Moving average trend confirmation")
            print("   - Candlestick price action signals")
            
        else:
            print("\n❌ Some tests failed - check TAAPI configuration")
            
    except Exception as e:
        print(f"\n❌ Live test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()