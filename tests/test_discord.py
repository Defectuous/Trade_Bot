#!/usr/bin/env python3
"""
Test script for Discord webhook functionality.
Run this to test your Discord webhook integration.
"""
import os
from dotenv import load_dotenv
from decimal import Decimal
from modules.discord_webhook import (
    send_trading_day_summary,
    send_trade_notification
)

def test_discord_webhook():
    """Test Discord webhook with sample data."""
    load_dotenv()
    webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
    
    if not webhook_url:
        print("❌ No Discord webhook URL configured")
        print("Add DISCORD_WEBHOOK_URL to your .env file to test")
        return False
    
    print("🔗 Discord webhook URL found, testing...")
    
    # Test trading day summary
    sample_wallet = Decimal("10000.50")
    sample_positions = {
        "AAPL": Decimal("10"),
        "TSLA": Decimal("5.5"),
        "SPY": Decimal("25")
    }
    
    print("📊 Sending sample trading day summary...")
    success1 = send_trading_day_summary(
        webhook_url, sample_wallet, sample_positions, "start"
    )
    
    # Test trade notification
    print("📈 Sending sample trade notification...")
    success2 = send_trade_notification(
        webhook_url, "BUY", "AAPL", Decimal("2"), Decimal("150.25")
    )
    
    if success1 and success2:
        print("✅ Discord webhook test completed successfully!")
        return True
    else:
        print("❌ Discord webhook test failed")
        return False

if __name__ == "__main__":
    test_discord_webhook()