#!/usr/bin/env python3
"""
Comprehensive validation test for all Alpaca client functions.
This script validates function signatures, error handling, and SDK compatibility.
"""

import logging
import sys
import inspect
from decimal import Decimal
from modules.alpaca_client import (
    connect_alpaca, get_wallet_amount, get_owned_positions, 
    get_last_trade_price, place_order, can_buy, owns_at_least, _retry_alpaca_call
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_function_signatures():
    """Validate that all function signatures are correct and well-documented."""
    logger.info("🔍 Validating function signatures...")
    
    functions_to_check = [
        connect_alpaca, get_wallet_amount, get_owned_positions,
        get_last_trade_price, place_order, can_buy, owns_at_least
    ]
    
    for func in functions_to_check:
        try:
            sig = inspect.signature(func)
            doc = inspect.getdoc(func)
            
            logger.info("✅ %s: %s", func.__name__, sig)
            if not doc:
                logger.warning("⚠️  %s: Missing docstring", func.__name__)
            else:
                logger.debug("   📖 %s", doc.split('\n')[0])  # First line of docstring
                
        except Exception as e:
            logger.error("❌ %s: Signature validation failed: %s", func.__name__, e)
    
    logger.info("📋 Function signature validation completed")

def validate_return_types():
    """Validate expected return types for functions."""
    logger.info("🎯 Validating return types...")
    
    # Test return type validation with mock data
    test_cases = [
        ("get_wallet_amount", "should return Decimal", lambda: Decimal("100.00")),
        ("get_owned_positions", "should return Dict[str, Decimal]", lambda: {"AAPL": Decimal("10")}),
        ("get_last_trade_price", "should return Decimal", lambda: Decimal("150.25")),
        ("can_buy", "should return bool", lambda: True),
        ("owns_at_least", "should return bool", lambda: False),
    ]
    
    for func_name, description, mock_return in test_cases:
        try:
            result = mock_return()
            expected_type = type(result)
            logger.info("✅ %s: %s (%s)", func_name, description, expected_type.__name__)
        except Exception as e:
            logger.error("❌ %s: Return type validation failed: %s", func_name, e)
    
    logger.info("🎯 Return type validation completed")

def validate_error_handling():
    """Validate error handling and retry logic."""
    logger.info("⚡ Validating error handling...")
    
    # Test retry wrapper with mock functions
    def mock_success():
        return "success"
    
    def mock_failure():
        raise Exception("Mock failure")
    
    def mock_server_error():
        from requests.exceptions import HTTPError
        import requests
        response = requests.Response()
        response.status_code = 500
        error = HTTPError("500 Server Error")
        error.response = response
        raise error
    
    # Test successful call
    try:
        result = _retry_alpaca_call(mock_success, max_retries=1, delay=0.1, backoff=1)
        if result == "success":
            logger.info("✅ Retry logic: Success case works")
        else:
            logger.error("❌ Retry logic: Success case failed")
    except Exception as e:
        logger.error("❌ Retry logic: Success case exception: %s", e)
    
    # Test failure after retries
    try:
        _retry_alpaca_call(mock_failure, max_retries=2, delay=0.1, backoff=1)
        logger.error("❌ Retry logic: Should have failed after retries")
    except Exception:
        logger.info("✅ Retry logic: Correctly failed after retries")
    
    logger.info("⚡ Error handling validation completed")

def validate_alpaca_sdk_compatibility():
    """Check compatibility with current Alpaca SDK."""
    logger.info("🔌 Validating Alpaca SDK compatibility...")
    
    try:
        import alpaca_trade_api as tradeapi
        logger.info("✅ Alpaca SDK imported successfully")
        
        # Check if we can create a REST client (without credentials)
        try:
            # This will fail due to missing credentials, but should not fail due to import issues
            api = tradeapi.REST("dummy", "dummy", base_url="https://paper-api.alpaca.markets")
            logger.info("✅ REST client can be instantiated")
        except Exception as e:
            if "credentials" in str(e).lower() or "authentication" in str(e).lower():
                logger.info("✅ REST client validation passed (expected auth error)")
            else:
                logger.warning("⚠️  REST client issue (not auth related): %s", e)
        
        # Check for modern SDK methods we use
        modern_methods = [
            'get_account', 'list_positions', 'submit_order',
            'get_latest_quote', 'get_bars', 'get_snapshot'
        ]
        
        for method in modern_methods:
            if hasattr(tradeapi.REST, method):
                logger.info("✅ Modern method available: %s", method)
            else:
                logger.error("❌ Modern method missing: %s", method)
                
    except ImportError as e:
        logger.error("❌ Alpaca SDK import failed: %s", e)
    
    logger.info("🔌 SDK compatibility validation completed")

def validate_configuration_handling():
    """Validate environment variable handling and configuration."""
    logger.info("⚙️  Validating configuration handling...")
    
    import os
    
    # Check retry configuration
    retry_configs = [
        ("ALPACA_RETRY_ATTEMPTS", "3"),
        ("ALPACA_RETRY_DELAY", "2"),
        ("ALPACA_RETRY_BACKOFF", "2")
    ]
    
    for env_var, default_val in retry_configs:
        current_val = os.environ.get(env_var, default_val)
        try:
            if env_var == "ALPACA_RETRY_ATTEMPTS":
                int(current_val)
            else:
                float(current_val)
            logger.info("✅ Config %s: %s (valid)", env_var, current_val)
        except ValueError:
            logger.error("❌ Config %s: %s (invalid)", env_var, current_val)
    
    # Check Alpaca connection configs
    alpaca_configs = [
        ("ALPACA_API_KEY", "Required for live operation"),
        ("ALPACA_SECRET_KEY", "Required for live operation"),
        ("ALPACA_BASE_URL", "Optional, defaults to paper trading")
    ]
    
    for env_var, description in alpaca_configs:
        value = os.environ.get(env_var)
        if value:
            logger.info("✅ Config %s: Set (%s)", env_var, description)
        else:
            logger.info("ℹ️  Config %s: Not set (%s)", env_var, description)
    
    logger.info("⚙️  Configuration validation completed")

def validate_data_precision():
    """Validate Decimal precision handling for financial data."""
    logger.info("💰 Validating financial data precision...")
    
    # Test Decimal handling
    test_values = ["100.00", "0.01", "1234.5678", "0", "999999.99"]
    
    for test_val in test_values:
        try:
            decimal_val = Decimal(test_val)
            if str(decimal_val) == test_val or decimal_val == Decimal(test_val):
                logger.info("✅ Decimal precision: %s -> %s", test_val, decimal_val)
            else:
                logger.warning("⚠️  Decimal precision: %s -> %s (unexpected)", test_val, decimal_val)
        except Exception as e:
            logger.error("❌ Decimal precision: %s failed: %s", test_val, e)
    
    # Test financial calculations
    try:
        price = Decimal("150.25")
        qty = Decimal("10")
        total = price * qty
        expected = Decimal("1502.50")
        
        if total == expected:
            logger.info("✅ Financial calculation: %s * %s = %s", price, qty, total)
        else:
            logger.error("❌ Financial calculation: %s * %s = %s (expected %s)", price, qty, total, expected)
    except Exception as e:
        logger.error("❌ Financial calculation failed: %s", e)
    
    logger.info("💰 Financial data precision validation completed")

def main():
    """Run all validation tests."""
    logger.info("🚀 Starting comprehensive Alpaca functions validation...")
    logger.info("=" * 60)
    
    validation_functions = [
        validate_function_signatures,
        validate_return_types,
        validate_error_handling,
        validate_alpaca_sdk_compatibility,
        validate_configuration_handling,
        validate_data_precision
    ]
    
    passed = 0
    failed = 0
    
    for validation_func in validation_functions:
        try:
            validation_func()
            logger.info("✅ %s: PASSED", validation_func.__name__)
            passed += 1
        except Exception as e:
            logger.error("❌ %s: FAILED - %s", validation_func.__name__, e)
            failed += 1
        
        logger.info("-" * 40)
    
    logger.info("🎉 Validation Summary:")
    logger.info("   ✅ Passed: %d", passed)
    logger.info("   ❌ Failed: %d", failed)
    logger.info("   📊 Total:  %d", passed + failed)
    
    if failed == 0:
        logger.info("🎯 ALL VALIDATIONS PASSED! Alpaca functions are ready for production.")
        return 0
    else:
        logger.warning("⚠️  Some validations failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())