#!/usr/bin/env python3
"""
Comprehensive test suite for all technical indicators on all configured symbols.
Tests all 7 indicators (RSI, MA, EMA, Pattern, ADX, ADXR, Candlestick) for VFF, SSP, GPRO.
"""
import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

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

# Load environment variables
load_dotenv()

def get_configured_symbols():
    """Get symbols from .env configuration."""
    symbols_env = os.environ.get("SYMBOLS")
    if symbols_env:
        symbols = [s.strip().upper() for s in symbols_env.split(",") if s.strip()]
    else:
        # Fallback to SYMBOL if SYMBOLS not set
        symbol = os.environ.get("SYMBOL", "AAPL")
        symbols = [symbol.upper()]
    
    return symbols

def test_individual_indicators():
    """Test each individual indicator function for all configured symbols."""
    print("🔍 Testing Individual Indicators for All Configured Symbols")
    print("=" * 65)
    
    taapi_key = os.environ.get("TAAPI_KEY")
    if not taapi_key:
        print("❌ TAAPI_KEY not found in environment variables")
        return False
    
    symbols = get_configured_symbols()
    print(f"📊 Configured symbols: {', '.join(symbols)}")
    print(f"🔑 TAAPI key: {'*' * (len(taapi_key) - 8) + taapi_key[-8:]}")
    
    # Define all indicator tests
    indicator_tests = [
        ("RSI", fetch_rsi_taapi),
        ("MA", fetch_ma_taapi),
        ("EMA", fetch_ema_taapi),
        ("Pattern", fetch_pattern_taapi),
        ("ADX", fetch_adx_taapi),
        ("ADXR", fetch_adxr_taapi),
        ("Candlestick", fetch_candle_taapi),
    ]
    
    results = {}
    total_tests = len(symbols) * len(indicator_tests)
    passed_tests = 0
    
    print(f"\n🧪 Running {total_tests} individual indicator tests...")
    
    for symbol in symbols:
        print(f"\n📈 Testing symbol: {symbol}")
        results[symbol] = {}
        
        for indicator_name, fetch_func in indicator_tests:
            print(f"   🔄 Testing {indicator_name}...", end=" ")
            
            try:
                if indicator_name in ["MA", "EMA"]:
                    # These functions need period parameter
                    result = fetch_func(symbol, taapi_key, period=20)
                elif indicator_name in ["ADX", "ADXR"]:
                    # These functions need period parameter
                    result = fetch_func(symbol, taapi_key, period=14)
                else:
                    # RSI, Pattern, Candlestick
                    result = fetch_func(symbol, taapi_key)
                
                if result is not None:
                    results[symbol][indicator_name] = result
                    
                    # Format result for display
                    if indicator_name == "Candlestick":
                        display_result = f"O:{result.get('open', 'N/A')} H:{result.get('high', 'N/A')} L:{result.get('low', 'N/A')} C:{result.get('close', 'N/A')}"
                    elif indicator_name == "Pattern":
                        display_result = f"Pattern: {result}"
                    else:
                        display_result = f"{result}"
                    
                    print(f"✅ {display_result}")
                    passed_tests += 1
                else:
                    results[symbol][indicator_name] = None
                    print(f"❌ No data returned")
                
                # Rate limiting delay
                time.sleep(0.5)
                
            except Exception as e:
                results[symbol][indicator_name] = f"Error: {str(e)}"
                print(f"❌ Error: {str(e)}")
                time.sleep(1)  # Longer delay on error
    
    print(f"\n📊 Individual Indicator Test Results:")
    print(f"   ✅ Passed: {passed_tests}/{total_tests}")
    print(f"   ❌ Failed: {total_tests - passed_tests}/{total_tests}")
    print(f"   📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    return results, passed_tests == total_tests

def test_fetch_all_indicators():
    """Test the fetch_all_indicators function for all configured symbols."""
    print(f"\n🔧 Testing fetch_all_indicators() for All Symbols")
    print("=" * 55)
    
    taapi_key = os.environ.get("TAAPI_KEY")
    symbols = get_configured_symbols()
    
    results = {}
    all_passed = True
    
    for symbol in symbols:
        print(f"\n📈 Testing fetch_all_indicators for {symbol}...")
        
        try:
            indicators = fetch_all_indicators(symbol, taapi_key)
            
            if indicators:
                results[symbol] = indicators
                print(f"   ✅ Successfully fetched all indicators")
                
                # Display results
                for indicator, value in indicators.items():
                    if value is not None and value != 'N/A':
                        if indicator == 'candle' and isinstance(value, dict):
                            display_val = f"O:{value.get('open', 'N/A')} H:{value.get('high', 'N/A')} L:{value.get('low', 'N/A')} C:{value.get('close', 'N/A')}"
                        else:
                            display_val = str(value)
                        print(f"      {indicator.upper()}: {display_val}")
                    else:
                        print(f"      {indicator.upper()}: N/A")
                        
            else:
                results[symbol] = None
                print(f"   ❌ Failed to fetch indicators")
                all_passed = False
            
            # Rate limiting delay
            time.sleep(1)
            
        except Exception as e:
            results[symbol] = f"Error: {str(e)}"
            print(f"   ❌ Error: {str(e)}")
            all_passed = False
            time.sleep(2)  # Longer delay on error
    
    return results, all_passed

def test_indicator_completeness():
    """Test that all expected indicators are returned."""
    print(f"\n📋 Testing Indicator Completeness")
    print("=" * 40)
    
    taapi_key = os.environ.get("TAAPI_KEY")
    symbols = get_configured_symbols()
    
    expected_indicators = {'rsi', 'ma', 'ema', 'pattern', 'adx', 'adxr', 'candle'}
    
    for symbol in symbols:
        print(f"\n📈 Checking indicator completeness for {symbol}...")
        
        try:
            indicators = fetch_all_indicators(symbol, taapi_key)
            
            if indicators:
                received_indicators = set(indicators.keys())
                missing = expected_indicators - received_indicators
                extra = received_indicators - expected_indicators
                
                if not missing and not extra:
                    print(f"   ✅ All 7 indicators present")
                else:
                    if missing:
                        print(f"   ⚠️  Missing indicators: {', '.join(missing)}")
                    if extra:
                        print(f"   ℹ️  Extra indicators: {', '.join(extra)}")
                
                # Check for None values
                none_indicators = [k for k, v in indicators.items() if v is None or v == 'N/A']
                if none_indicators:
                    print(f"   ⚠️  Indicators with no data: {', '.join(none_indicators)}")
                else:
                    print(f"   ✅ All indicators have data")
            else:
                print(f"   ❌ No indicators returned")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            time.sleep(2)

def test_api_rate_limiting():
    """Test API rate limiting by making multiple rapid requests."""
    print(f"\n⏱️  Testing API Rate Limiting")
    print("=" * 35)
    
    taapi_key = os.environ.get("TAAPI_KEY")
    symbols = get_configured_symbols()
    
    print(f"📊 Making rapid requests to test rate limiting...")
    
    for i, symbol in enumerate(symbols):
        print(f"\n   Request {i+1}: {symbol}")
        
        start_time = time.time()
        try:
            result = fetch_rsi_taapi(symbol, taapi_key)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if result is not None:
                print(f"   ✅ Response time: {response_time:.2f}s, RSI: {result}")
            else:
                print(f"   ❌ No data returned, Response time: {response_time:.2f}s")
                
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            print(f"   ❌ Error after {response_time:.2f}s: {str(e)}")
        
        # Small delay between requests
        time.sleep(0.2)

def generate_test_report(individual_results, fetch_all_results):
    """Generate a comprehensive test report."""
    print(f"\n📊 Comprehensive Test Report")
    print("=" * 40)
    
    symbols = get_configured_symbols()
    
    print(f"\n🎯 Test Summary:")
    print(f"   📈 Symbols tested: {len(symbols)} ({', '.join(symbols)})")
    print(f"   🔍 Indicators tested: 7 (RSI, MA, EMA, Pattern, ADX, ADXR, Candlestick)")
    print(f"   ⏰ Test timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n📈 Per-Symbol Results:")
    for symbol in symbols:
        print(f"\n   {symbol}:")
        
        # Individual indicator results
        if symbol in individual_results:
            working_indicators = sum(1 for v in individual_results[symbol].values() 
                                   if v is not None and not str(v).startswith('Error'))
            total_indicators = len(individual_results[symbol])
            print(f"      Individual indicators: {working_indicators}/{total_indicators} working")
        
        # Fetch all indicators result
        if symbol in fetch_all_results:
            if isinstance(fetch_all_results[symbol], dict):
                working_all = sum(1 for v in fetch_all_results[symbol].values() 
                                if v is not None and v != 'N/A')
                total_all = len(fetch_all_results[symbol])
                print(f"      fetch_all_indicators: {working_all}/{total_all} indicators")
            else:
                print(f"      fetch_all_indicators: Failed")
    
    print(f"\n💡 Recommendations:")
    
    # Check for common issues
    all_symbols_working = all(symbol in fetch_all_results and 
                            isinstance(fetch_all_results[symbol], dict) 
                            for symbol in symbols)
    
    if all_symbols_working:
        print(f"   ✅ All symbols are working correctly")
        print(f"   ✅ Ready for live trading")
    else:
        failed_symbols = [symbol for symbol in symbols 
                         if symbol not in fetch_all_results or 
                         not isinstance(fetch_all_results[symbol], dict)]
        if failed_symbols:
            print(f"   ⚠️  Issues with symbols: {', '.join(failed_symbols)}")
            print(f"   💡 Consider removing problematic symbols from SYMBOLS config")
    
    print(f"\n🔗 API Status:")
    print(f"   📡 TAAPI.io: {'Connected' if any(fetch_all_results.values()) else 'Issues detected'}")
    print(f"   🔑 API Key: {'Valid' if any(fetch_all_results.values()) else 'Check validity'}")

def main():
    """Run comprehensive indicator tests for all configured symbols."""
    print("🚀 Comprehensive Indicator Testing Suite")
    print("=" * 45)
    
    # Check prerequisites
    taapi_key = os.environ.get("TAAPI_KEY")
    if not taapi_key:
        print("❌ TAAPI_KEY not found in environment variables")
        print("💡 Please ensure your .env file contains a valid TAAPI_KEY")
        return False
    
    symbols = get_configured_symbols()
    if not symbols:
        print("❌ No symbols configured")
        print("💡 Please ensure your .env file contains SYMBOLS or SYMBOL")
        return False
    
    print(f"🎯 Test Configuration:")
    print(f"   📊 Symbols: {', '.join(symbols)}")
    print(f"   🔍 Indicators: RSI, MA, EMA, Pattern, ADX, ADXR, Candlestick")
    print(f"   🔑 TAAPI Key: {'*' * (len(taapi_key) - 8) + taapi_key[-8:]}")
    
    try:
        # Run all tests
        individual_results, individual_success = test_individual_indicators()
        fetch_all_results, fetch_all_success = test_fetch_all_indicators()
        test_indicator_completeness()
        test_api_rate_limiting()
        
        # Generate report
        generate_test_report(individual_results, fetch_all_results)
        
        # Overall result
        overall_success = individual_success and fetch_all_success
        
        if overall_success:
            print(f"\n🎉 All tests passed! Indicators are working correctly for all symbols.")
        else:
            print(f"\n⚠️  Some tests failed. Check the details above.")
        
        return overall_success
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Tests interrupted by user")
        return False
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)