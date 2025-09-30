#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced Alpaca client retry logic.
This can be run on your Raspberry Pi to test the error handling.
"""

import logging
import sys
from modules.alpaca_client import connect_alpaca, get_wallet_amount, get_owned_positions, get_last_trade_price

# Set up logging to see retry attempts
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_alpaca_retry():
    """Test the enhanced Alpaca client with retry logic."""
    logger = logging.getLogger(__name__)
    
    try:
        # Connect to Alpaca
        logger.info("🔌 Connecting to Alpaca...")
        api = connect_alpaca()
        logger.info("✅ Alpaca connection successful")
        
        # Test wallet amount calls with retry logic
        logger.info("💰 Testing wallet amount calls...")
        
        try:
            cash = get_wallet_amount(api, 'cash')
            logger.info("✅ Cash balance: $%s", cash)
        except Exception as e:
            logger.error("❌ Cash fetch failed after retries: %s", e)
            
        try:
            buying_power = get_wallet_amount(api, 'buying_power')
            logger.info("✅ Buying power: $%s", buying_power)
        except Exception as e:
            logger.error("❌ Buying power fetch failed after retries: %s", e)
            
        try:
            portfolio_value = get_wallet_amount(api, 'portfolio_value')
            logger.info("✅ Portfolio value: $%s", portfolio_value)
        except Exception as e:
            logger.error("❌ Portfolio value fetch failed after retries: %s", e)
            
        # Test positions call
        logger.info("📊 Testing positions call...")
        try:
            positions = get_owned_positions(api)
            logger.info("✅ Positions fetched: %d positions", len(positions))
            for symbol, qty in positions.items():
                logger.info("  📈 %s: %s shares", symbol, qty)
        except Exception as e:
            logger.error("❌ Positions fetch failed after retries: %s", e)
            
        # Test price fetching with modern SDK methods
        logger.info("💲 Testing price fetching with updated methods...")
        test_symbols = ['AAPL', 'SPY']
        
        for symbol in test_symbols:
            try:
                price = get_last_trade_price(api, symbol)
                logger.info("✅ %s price: $%s", symbol, price)
            except Exception as e:
                logger.error("❌ Price fetch failed for %s: %s", symbol, e)
            
        logger.info("🎉 All tests completed!")
        
    except Exception as e:
        logger.error("❌ Failed to connect to Alpaca: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    test_alpaca_retry()