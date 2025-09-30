#!/usr/bin/env python3
"""
Test script to verify the updated Alpaca price fetching methods.
This tests the new get_last_trade_price function with modern Alpaca SDK.
"""

import logging
import sys
from decimal import Decimal
from modules.alpaca_client import connect_alpaca, get_last_trade_price

# Set up logging to see the fallback attempts
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_price_fetching():
    """Test the updated price fetching with modern Alpaca SDK methods."""
    logger = logging.getLogger(__name__)
    
    # Test symbols to try
    test_symbols = ['AAPL', 'SPY', 'TSLA']
    
    try:
        # Connect to Alpaca
        logger.info("🔌 Connecting to Alpaca...")
        api = connect_alpaca()
        logger.info("✅ Alpaca connection successful")
        
        logger.info("💰 Testing price fetching with modern SDK methods...")
        
        for symbol in test_symbols:
            try:
                logger.info("📊 Fetching price for %s...", symbol)
                price = get_last_trade_price(api, symbol)
                logger.info("✅ %s price: $%s", symbol, price)
                
                # Verify price is reasonable (positive number)
                if price > 0:
                    logger.info("✅ Price validation passed for %s", symbol)
                else:
                    logger.warning("⚠️ Suspicious price for %s: $%s", symbol, price)
                    
            except Exception as e:
                logger.error("❌ Failed to fetch price for %s: %s", symbol, e)
                
        logger.info("🎉 Price fetching test completed!")
        
    except Exception as e:
        logger.error("❌ Failed to connect to Alpaca or test failed: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    test_price_fetching()