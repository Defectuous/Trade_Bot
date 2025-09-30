#!/bin/bash
# Quick fix script for Alpaca authentication issues

echo "🔧 ALPACA AUTHENTICATION TROUBLESHOOTER"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "trade_bot.py" ]; then
    echo "❌ Please run this script from the TradeBot directory"
    echo "   cd /home/defectuous/TradeBot"
    echo "   ./fix_alpaca_auth.sh"
    exit 1
fi

echo -e "\n1. 🔍 Checking current .env configuration..."

if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "   Copy from .env.example and configure your keys"
    exit 1
fi

# Check for required variables
echo "   Checking ALPACA_API_KEY..."
if grep -q "ALPACA_API_KEY=" .env; then
    API_KEY=$(grep "ALPACA_API_KEY=" .env | cut -d'=' -f2)
    if [ ${#API_KEY} -gt 10 ]; then
        echo "   ✅ API Key found (${#API_KEY} chars)"
    else
        echo "   ⚠️  API Key seems too short"
    fi
else
    echo "   ❌ ALPACA_API_KEY not found in .env"
fi

echo "   Checking ALPACA_SECRET_KEY..."
if grep -q "ALPACA_SECRET_KEY=" .env; then
    SECRET_KEY=$(grep "ALPACA_SECRET_KEY=" .env | cut -d'=' -f2)
    if [ ${#SECRET_KEY} -gt 20 ]; then
        echo "   ✅ Secret Key found (${#SECRET_KEY} chars)"
    else
        echo "   ⚠️  Secret Key seems too short"
    fi
else
    echo "   ❌ ALPACA_SECRET_KEY not found in .env"
fi

echo "   Checking ALPACA_BASE_URL..."
if grep -q "ALPACA_BASE_URL=" .env; then
    BASE_URL=$(grep "ALPACA_BASE_URL=" .env | cut -d'=' -f2)
    echo "   Current URL: $BASE_URL"
    if [[ "$BASE_URL" == *"paper-api"* ]]; then
        echo "   ✅ Paper trading endpoint (good for testing)"
    elif [[ "$BASE_URL" == *"api.alpaca.markets"* ]]; then
        echo "   ⚠️  Live trading endpoint - make sure this is intentional"
    else
        echo "   ❌ Invalid or missing URL"
    fi
else
    echo "   ❌ ALPACA_BASE_URL not found in .env"
fi

echo -e "\n2. 🧪 Testing API connection..."

# Activate virtual environment and test
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "   Virtual environment activated"
    
    # Test if we can import required modules
    python3 -c "import alpaca_trade_api; print('   ✅ alpaca-trade-api module available')" 2>/dev/null || {
        echo "   ❌ alpaca-trade-api not installed"
        echo "   Installing..."
        pip install alpaca-trade-api
    }
    
    # Run the diagnostic script if it exists
    if [ -f "test_alpaca_auth.py" ]; then
        echo "   Running connection test..."
        python3 test_alpaca_auth.py
    else
        echo "   ⚠️  Diagnostic script not found, testing basic connection..."
        python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()

try:
    import alpaca_trade_api as tradeapi
    api = tradeapi.REST(
        key_id=os.environ.get('ALPACA_API_KEY'),
        secret_key=os.environ.get('ALPACA_SECRET_KEY'),
        base_url=os.environ.get('ALPACA_BASE_URL'),
        api_version='v2'
    )
    account = api.get_account()
    print(f'   ✅ Connection successful! Account: {account.id}')
    print(f'   Cash: \${account.cash}, Status: {account.status}')
except Exception as e:
    print(f'   ❌ Connection failed: {e}')
    if 'unauthorized' in str(e).lower():
        print('   💡 Authentication issue - check your API keys')
"
    fi
else
    echo "   ❌ Virtual environment not found (.venv directory missing)"
    echo "   Please recreate the virtual environment:"
    echo "   python3 -m venv .venv"
    echo "   source .venv/bin/activate"
    echo "   pip install -r requirements.txt"
fi

echo -e "\n3. 🔧 Common Solutions:"
echo "   📝 Check API keys at: https://alpaca.markets (Paper Trading section)"
echo "   🔄 Restart service: sudo systemctl restart trade_bot.service"
echo "   📊 View logs: sudo journalctl -u trade_bot.service -f"
echo "   🧪 Test connection: python3 test_alpaca_auth.py"

echo -e "\n4. 📋 Service Status:"
systemctl is-active trade_bot.service >/dev/null 2>&1 && {
    echo "   ✅ Service is running"
} || {
    echo "   ⚠️  Service is not running"
    echo "   Start with: sudo systemctl start trade_bot.service"
}

echo -e "\n💡 Next Steps:"
echo "   1. Fix any issues shown above"
echo "   2. Restart the service if needed"
echo "   3. Monitor logs for success: sudo journalctl -u trade_bot.service -f"
echo "   4. Contact support if issues persist"