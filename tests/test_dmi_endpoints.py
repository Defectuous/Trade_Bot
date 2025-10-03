#!/usr/bin/env python3
"""Test DMI endpoint with different possible names."""

import os
import sys
import requests
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

def test_dmi_endpoints():
    """Test different possible DMI endpoint names."""
    taapi_key = os.getenv('TAAPI_KEY')
    if not taapi_key:
        print("❌ TAAPI_KEY not found")
        return
    
    symbol = "AAPL"
    interval = "1m"
    period = 14
    
    # List of possible DMI endpoint names to try
    endpoints = [
        "dmi",
        "dx", 
        "di",
        "directional",
        "plus_di",
        "minus_di",
        "pdm",
        "mdm"
    ]
    
    print(f"🔍 Testing DMI-related endpoints for {symbol}")
    print("=" * 50)
    
    for endpoint in endpoints:
        print(f"\n🧪 Testing endpoint: {endpoint}")
        url = f"https://api.taapi.io/{endpoint}"
        params = {
            "secret": taapi_key, 
            "symbol": symbol, 
            "interval": interval, 
            "type": "stocks", 
            "period": period
        }
        
        try:
            resp = requests.get(url, params=params, timeout=10)
            print(f"   Status: {resp.status_code}")
            
            if resp.status_code == 200:
                data = resp.json()
                print(f"   ✅ Success: {data}")
            else:
                print(f"   ❌ Error: {resp.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("🔍 DMI endpoint testing completed!")

if __name__ == "__main__":
    test_dmi_endpoints()