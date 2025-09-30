#!/usr/bin/env python3
"""Alpaca API Connection Diagnostic Script."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_alpaca_connection():
    """Test Alpaca API connection and diagnose authentication issues."""
    
    print("🔍 ALPACA API CONNECTION DIAGNOSTICS")
    print("=" * 50)
    
    # Check environment variables
    alpaca_key = os.environ.get("ALPACA_API_KEY")
    alpaca_secret = os.environ.get("ALPACA_SECRET_KEY") 
    alpaca_url = os.environ.get("ALPACA_BASE_URL")
    
    print(f"\n📋 Configuration Check:")
    print(f"   ALPACA_API_KEY: {'✅ Set' if alpaca_key else '❌ Missing'}")
    print(f"   ALPACA_SECRET_KEY: {'✅ Set' if alpaca_secret else '❌ Missing'}")
    print(f"   ALPACA_BASE_URL: {alpaca_url if alpaca_url else '❌ Missing'}")
    
    if alpaca_key:
        print(f"   API Key Preview: {alpaca_key[:8]}...{alpaca_key[-4:] if len(alpaca_key) > 12 else 'TOO_SHORT'}")
    
    # Check URL configuration
    if alpaca_url:
        if "paper-api" in alpaca_url:
            print(f"   ✅ Paper Trading Mode: {alpaca_url}")
        elif "api.alpaca.markets" in alpaca_url:
            print(f"   ⚠️  LIVE Trading Mode: {alpaca_url}")
            print(f"   💡 Recommendation: Use paper trading for testing")
        else:
            print(f"   ❌ Invalid URL: {alpaca_url}")
    
    if not all([alpaca_key, alpaca_secret, alpaca_url]):
        print("\n❌ Missing required Alpaca credentials!")
        return False
    
    # Test API connection
    try:
        print(f"\n🔌 Testing API Connection...")
        
        # Import Alpaca
        try:
            import alpaca_trade_api as tradeapi
        except ImportError:
            print("❌ alpaca-trade-api not installed!")
            print("   Run: pip install alpaca-trade-api")
            return False
        
        # Create API client
        api = tradeapi.REST(
            key_id=alpaca_key,
            secret_key=alpaca_secret,
            base_url=alpaca_url,
            api_version='v2'
        )
        
        # Test account access
        print("   Testing account access...")
        account = api.get_account()
        print(f"   ✅ Account connected successfully!")
        print(f"   Account ID: {account.id}")
        print(f"   Status: {account.status}")
        print(f"   Cash: ${account.cash}")
        print(f"   Buying Power: ${account.buying_power}")
        
        # Test market data access
        print(f"\n📊 Testing market data access...")
        try:
            quote = api.get_latest_quote("AAPL")
            print(f"   ✅ Market data accessible")
            print(f"   AAPL Quote: ${quote.bid} / ${quote.ask}")
        except Exception as e:
            print(f"   ⚠️  Market data issue: {e}")
        
        # Test order permissions (dry run)
        print(f"\n🛒 Testing order permissions...")
        try:
            # Try to get existing orders (safe operation)
            orders = api.list_orders(status='all', limit=1)
            print(f"   ✅ Order API accessible ({len(orders)} recent orders)")
        except Exception as e:
            print(f"   ❌ Order permission issue: {e}")
            if "unauthorized" in str(e).lower():
                print(f"   💡 This suggests authentication problems!")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        
        # Provide specific error guidance
        error_str = str(e).lower()
        if "unauthorized" in error_str:
            print(f"\n🔧 AUTHENTICATION ERROR DETECTED:")
            print(f"   1. Verify your API keys are correct")
            print(f"   2. Check if keys are for paper or live trading")
            print(f"   3. Ensure keys haven't expired")
            print(f"   4. Try generating new keys at alpaca.markets")
        elif "forbidden" in error_str:
            print(f"\n🔧 PERMISSION ERROR DETECTED:")
            print(f"   1. Your API keys may not have trading permissions")
            print(f"   2. Check your Alpaca account settings")
        elif "not found" in error_str:
            print(f"\n🔧 ENDPOINT ERROR DETECTED:")
            print(f"   1. Check your ALPACA_BASE_URL")
            print(f"   2. Should be: https://paper-api.alpaca.markets")
        
        return False

def provide_solutions():
    """Provide step-by-step solutions."""
    
    print(f"\n\n🔧 STEP-BY-STEP SOLUTIONS:")
    print("=" * 35)
    
    print(f"\n1. 🔑 CHECK YOUR API KEYS:")
    print(f"   • Log into https://alpaca.markets")
    print(f"   • Go to 'Paper Trading' section")
    print(f"   • Generate new API keys if needed")
    print(f"   • Copy EXACT values (no extra spaces)")
    
    print(f"\n2. 📝 UPDATE YOUR .env FILE:")
    print(f"   • Edit: /home/defectuous/TradeBot/.env")
    print(f"   • Ensure format: ALPACA_API_KEY=PK123...")
    print(f"   • Ensure format: ALPACA_SECRET_KEY=xyz...")
    print(f"   • Use paper URL: https://paper-api.alpaca.markets")
    
    print(f"\n3. 🔄 RESTART THE SERVICE:")
    print(f"   sudo systemctl restart trade_bot.service")
    print(f"   sudo journalctl -u trade_bot.service -f")
    
    print(f"\n4. 🧪 TEST AGAIN:")
    print(f"   cd /home/defectuous/TradeBot")
    print(f"   source .venv/bin/activate")
    print(f"   python test_alpaca_auth.py")

if __name__ == "__main__":
    success = test_alpaca_connection()
    provide_solutions()
    
    if success:
        print(f"\n✅ Alpaca connection successful!")
        print(f"   Your authentication error may be intermittent.")
        print(f"   Monitor the service logs for more details.")
    else:
        print(f"\n❌ Connection failed - follow solutions above")
        sys.exit(1)