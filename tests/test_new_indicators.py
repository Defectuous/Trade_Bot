#!/usr/bin/env python3
"""Test script for new TAAPI indicators: Volume, Bollinger Bands, and DMI."""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv not installed, trying to read .env manually")
    env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

from modules.taapi import (
    fetch_volume_taapi, 
    fetch_bbands_taapi, 
    fetch_dmi_taapi, 
    fetch_all_indicators
)
from decimal import Decimal

def test_new_indicators():
    """Test the three new indicators with AAPL."""
    taapi_key = os.getenv('TAAPI_KEY')
    if not taapi_key:
        print("❌ TAAPI_KEY not found in environment variables")
        return False
    
    symbol = "AAPL"
    print(f"🧪 Testing new indicators for {symbol}")
    print("=" * 50)
    
    # Test Volume
    print("\n📊 Testing Volume Indicator:")
    try:
        volume = fetch_volume_taapi(symbol, taapi_key)
        if volume:
            print(f"✅ Volume: {volume:,}")
        else:
            print("❌ Volume: Failed to fetch")
    except Exception as e:
        print(f"❌ Volume error: {e}")
    
    # Test Bollinger Bands
    print("\n📈 Testing Bollinger Bands:")
    try:
        bbands = fetch_bbands_taapi(symbol, taapi_key)
        if bbands:
            print(f"✅ Bollinger Bands:")
            print(f"   Upper Band: {bbands['upper']}")
            print(f"   Middle Band: {bbands['middle']}")
            print(f"   Lower Band: {bbands['lower']}")
        else:
            print("❌ Bollinger Bands: Failed to fetch")
    except Exception as e:
        print(f"❌ Bollinger Bands error: {e}")
    
    # Test DMI
    print("\n🎯 Testing DMI (Directional Movement Index):")
    try:
        dmi = fetch_dmi_taapi(symbol, taapi_key)
        if dmi:
            print(f"✅ DMI:")
            print(f"   DI+ (Plus): {dmi['di_plus']}")
            print(f"   DI- (Minus): {dmi['di_minus']}")
            print(f"   ADX: {dmi['adx']}")
        else:
            print("❌ DMI: Failed to fetch")
    except Exception as e:
        print(f"❌ DMI error: {e}")
    
    # Test all indicators together
    print("\n🔄 Testing fetch_all_indicators with new indicators:")
    try:
        # Enable the new indicators for testing
        os.environ['ENABLE_VOLUME'] = 'true'
        os.environ['ENABLE_BBANDS'] = 'true'
        os.environ['ENABLE_DMI'] = 'true'
        
        all_indicators = fetch_all_indicators(symbol, taapi_key)
        
        print(f"✅ All indicators fetched successfully!")
        print(f"   Total indicators: {len([k for k, v in all_indicators.items() if v is not None])}")
        
        # Show new indicators
        if all_indicators.get('volume'):
            print(f"   📊 Volume: {all_indicators['volume']:,}")
        if all_indicators.get('bbands'):
            bbands = all_indicators['bbands']
            print(f"   📈 BBands: U:{bbands['upper']} M:{bbands['middle']} L:{bbands['lower']}")
        if all_indicators.get('dmi'):
            dmi = all_indicators['dmi']
            print(f"   🎯 DMI: DI+:{dmi['di_plus']} DI-:{dmi['di_minus']} ADX:{dmi['adx']}")
            
    except Exception as e:
        print(f"❌ fetch_all_indicators error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 New indicator testing completed!")
    
    return True

if __name__ == "__main__":
    test_new_indicators()