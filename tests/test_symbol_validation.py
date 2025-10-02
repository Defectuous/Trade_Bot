#!/usr/bin/env python3
"""
Quick test to validate which symbols work with TAAPI before running comprehensive tests.
Tests both configured symbols and common reliable symbols.
"""
import os
import sys
import time
from dotenv import load_dotenv

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.taapi import fetch_rsi_taapi, fetch_all_indicators

# Load environment variables
load_dotenv()

def test_symbol_availability():
    """Test symbol availability and data quality."""
    print("🔍 Testing Symbol Availability and Data Quality")
    print("=" * 50)
    
    taapi_key = os.environ.get("TAAPI_KEY")
    if not taapi_key:
        print("❌ TAAPI_KEY not found in environment variables")
        return False
    
    # Get configured symbols
    symbols_env = os.environ.get("SYMBOLS")
    if symbols_env:
        configured_symbols = [s.strip().upper() for s in symbols_env.split(",") if s.strip()]
    else:
        configured_symbols = [os.environ.get("SYMBOL", "AAPL").upper()]
    
    # Common reliable symbols for comparison
    reliable_symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "SPY", "QQQ"]
    
    print(f"🎯 Configured symbols: {', '.join(configured_symbols)}")
    print(f"🔗 Reliable symbols for comparison: {', '.join(reliable_symbols)}")
    
    def test_symbols(symbol_list, category_name):
        print(f"\n📊 Testing {category_name}:")
        results = {}
        
        for symbol in symbol_list:
            print(f"   🔄 Testing {symbol}...", end=" ")
            
            try:
                # Test RSI first (quickest indicator)
                rsi = fetch_rsi_taapi(symbol, taapi_key)
                
                if rsi is not None:
                    print(f"✅ RSI: {rsi}")
                    results[symbol] = "Working"
                    
                    # Quick test of fetch_all_indicators
                    try:
                        indicators = fetch_all_indicators(symbol, taapi_key)
                        if indicators:
                            working_indicators = sum(1 for v in indicators.values() 
                                                   if v is not None and v != 'N/A')
                            print(f"      📈 All indicators: {working_indicators}/7 working")
                        else:
                            print(f"      ⚠️  fetch_all_indicators failed")
                    except Exception as e:
                        print(f"      ⚠️  fetch_all_indicators error: {str(e)[:50]}")
                else:
                    print(f"❌ No RSI data available")
                    results[symbol] = "No data"
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Error: {str(e)[:50]}")
                results[symbol] = f"Error: {str(e)[:50]}"
                time.sleep(1)  # Longer delay on error
        
        return results
    
    # Test reliable symbols first
    reliable_results = test_symbols(reliable_symbols[:3], "Reliable Symbols (for API validation)")
    
    # Test configured symbols
    configured_results = test_symbols(configured_symbols, "Configured Symbols")
    
    # Analysis
    print(f"\n📋 Results Summary:")
    
    reliable_working = sum(1 for r in reliable_results.values() if r == "Working")
    configured_working = sum(1 for r in configured_results.values() if r == "Working")
    
    print(f"   🔗 Reliable symbols working: {reliable_working}/{len(reliable_results)}")
    print(f"   🎯 Configured symbols working: {configured_working}/{len(configured_results)}")
    
    if reliable_working == 0:
        print(f"\n❌ CRITICAL: No reliable symbols working - API issue detected")
        print(f"   💡 Check TAAPI_KEY validity and account status")
        return False
    elif reliable_working < len(reliable_results):
        print(f"\n⚠️  Some reliable symbols not working - possible API limitations")
    else:
        print(f"\n✅ API is working correctly with reliable symbols")
    
    if configured_working == 0:
        print(f"\n⚠️  ISSUE: None of your configured symbols are working")
        print(f"   💡 Consider using more liquid symbols like: AAPL, MSFT, SPY")
        print(f"   💡 Current configured symbols: {', '.join(configured_symbols)}")
        
        # Suggest replacements
        working_reliable = [symbol for symbol, result in reliable_results.items() if result == "Working"]
        if working_reliable:
            suggested = working_reliable[:len(configured_symbols)]
            print(f"   💡 Suggested replacement: SYMBOLS={', '.join(suggested)}")
    elif configured_working < len(configured_symbols):
        not_working = [symbol for symbol, result in configured_results.items() if result != "Working"]
        print(f"\n⚠️  Some configured symbols not working: {', '.join(not_working)}")
        print(f"   💡 Consider replacing non-working symbols")
    else:
        print(f"\n✅ All configured symbols are working correctly!")
    
    return configured_working > 0

def quick_comprehensive_test():
    """Run a quick comprehensive test on working symbols."""
    print(f"\n🚀 Quick Comprehensive Test")
    print("=" * 30)
    
    taapi_key = os.environ.get("TAAPI_KEY")
    
    # Use a mix of reliable and configured symbols
    test_symbols = ["AAPL"]  # Start with one reliable symbol
    
    # Add configured symbols
    symbols_env = os.environ.get("SYMBOLS")
    if symbols_env:
        configured = [s.strip().upper() for s in symbols_env.split(",") if s.strip()]
        test_symbols.extend(configured[:2])  # Limit to avoid too many API calls
    
    print(f"📊 Testing symbols: {', '.join(test_symbols)}")
    
    for symbol in test_symbols:
        print(f"\n📈 {symbol}:")
        
        try:
            indicators = fetch_all_indicators(symbol, taapi_key)
            
            if indicators:
                for name, value in indicators.items():
                    if value is not None and value != 'N/A':
                        if name == 'candle' and isinstance(value, dict):
                            print(f"   {name.upper()}: O:{value.get('open', 'N/A')} C:{value.get('close', 'N/A')}")
                        else:
                            print(f"   {name.upper()}: {value}")
                    else:
                        print(f"   {name.upper()}: No data")
            else:
                print(f"   ❌ No indicators returned")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            time.sleep(2)

if __name__ == "__main__":
    print("🧪 Symbol Validation and Quick Testing")
    print("=" * 45)
    
    try:
        success = test_symbol_availability()
        
        if success:
            quick_comprehensive_test()
            print(f"\n✅ Testing completed successfully!")
        else:
            print(f"\n❌ Issues detected - check configuration and API status")
            
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()