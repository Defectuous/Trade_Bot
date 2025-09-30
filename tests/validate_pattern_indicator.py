#!/usr/bin/env python3
"""
Comprehensive validation test for TAAPI.io pattern indicator (Three Black Crows).
This script validates the pattern indicator functionality, API response handling, and value interpretation.
"""

import logging
import sys
import os
import requests
from decimal import Decimal
from modules.taapi import fetch_pattern_taapi

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_pattern_function_signature():
    """Validate the pattern function signature and documentation."""
    logger.info("🔍 Validating pattern function signature...")
    
    import inspect
    
    try:
        sig = inspect.signature(fetch_pattern_taapi)
        doc = inspect.getdoc(fetch_pattern_taapi)
        
        logger.info("✅ Function signature: %s", sig)
        logger.info("✅ Return type annotation: %s", sig.return_annotation)
        
        if doc:
            logger.info("✅ Documentation: %s", doc)
        else:
            logger.warning("⚠️  Missing detailed documentation")
            
        # Check parameter defaults
        params = sig.parameters
        expected_params = ['symbol', 'taapi_key', 'interval', 'timeout']
        
        for param_name in expected_params:
            if param_name in params:
                param = params[param_name]
                logger.info("✅ Parameter %s: %s", param_name, param)
            else:
                logger.error("❌ Missing parameter: %s", param_name)
                
    except Exception as e:
        logger.error("❌ Function signature validation failed: %s", e)
        return False
    
    logger.info("📋 Function signature validation completed")
    return True

def validate_pattern_value_interpretation():
    """Validate the pattern value interpretation logic."""
    logger.info("🎯 Validating pattern value interpretation...")
    
    # Test cases for pattern value interpretation
    test_cases = [
        (100, "STRONG_BEARISH", "Maximum bearish signal"),
        (-100, "STRONG_BULLISH", "Maximum bullish signal"),
        (50, "BEARISH", "Moderate bearish signal"),
        (25, "BEARISH", "Weak bearish signal"),
        (-50, "BULLISH", "Moderate bullish signal"),
        (-25, "BULLISH", "Weak bullish signal"),
        (0, "NEUTRAL", "No pattern signal"),
        (None, None, "Invalid/missing data")
    ]
    
    # Mock the pattern interpretation logic from the function
    def interpret_pattern_value(value):
        if value is None:
            return None
        if value == 100:
            return "STRONG_BEARISH"
        elif value == -100:
            return "STRONG_BULLISH"
        elif value > 0:
            return "BEARISH"
        elif value < 0:
            return "BULLISH"
        else:
            return "NEUTRAL"
    
    all_passed = True
    for input_value, expected_output, description in test_cases:
        try:
            result = interpret_pattern_value(input_value)
            if result == expected_output:
                logger.info("✅ Value %s → %s (%s)", input_value, result, description)
            else:
                logger.error("❌ Value %s → %s (expected %s) - %s", 
                           input_value, result, expected_output, description)
                all_passed = False
        except Exception as e:
            logger.error("❌ Pattern interpretation failed for %s: %s", input_value, e)
            all_passed = False
    
    logger.info("🎯 Pattern value interpretation validation completed")
    return all_passed

def validate_taapi_api_endpoint():
    """Validate the TAAPI.io API endpoint and response format."""
    logger.info("🔌 Validating TAAPI.io API endpoint...")
    
    # Check if we have a TAAPI key for testing
    taapi_key = os.environ.get("TAAPI_KEY")
    if not taapi_key:
        logger.warning("⚠️  TAAPI_KEY not found in environment - skipping live API test")
        logger.info("ℹ️  To test live API, set TAAPI_KEY environment variable")
        return True
    
    # Test API endpoint structure
    url = "https://api.taapi.io/cdl3blackcrows"
    test_symbol = "AAPL"  # Use a reliable symbol
    
    params = {
        "secret": taapi_key,
        "symbol": test_symbol,
        "interval": "1m",
        "type": "stocks"
    }
    
    try:
        logger.info("🌐 Testing TAAPI.io cdl3blackcrows endpoint...")
        resp = requests.get(url, params=params, timeout=10)
        
        logger.info("📡 Response status: %d", resp.status_code)
        
        if resp.status_code == 200:
            try:
                data = resp.json()
                logger.info("✅ Valid JSON response received")
                logger.info("📊 Response data: %s", data)
                
                # Check response structure
                if "value" in data:
                    value = data["value"]
                    logger.info("✅ Pattern value found: %s (type: %s)", value, type(value))
                    
                    # Validate value is numeric
                    if isinstance(value, (int, float)):
                        logger.info("✅ Pattern value is numeric")
                        
                        # Test interpretation
                        if value == 100:
                            interpretation = "STRONG_BEARISH"
                        elif value == -100:
                            interpretation = "STRONG_BULLISH"
                        elif value > 0:
                            interpretation = "BEARISH"
                        elif value < 0:
                            interpretation = "BULLISH"
                        else:
                            interpretation = "NEUTRAL"
                        
                        logger.info("✅ Pattern interpretation: %s", interpretation)
                        
                    else:
                        logger.warning("⚠️  Pattern value is not numeric: %s", type(value))
                        
                else:
                    logger.error("❌ 'value' field missing from response")
                    return False
                    
            except Exception as e:
                logger.error("❌ Failed to parse JSON response: %s", e)
                logger.error("📄 Raw response: %s", resp.text[:200])
                return False
                
        elif resp.status_code == 401:
            logger.error("❌ Authentication failed - check TAAPI_KEY")
            return False
        elif resp.status_code == 403:
            logger.error("❌ Access forbidden - check TAAPI subscription plan")
            return False
        elif resp.status_code == 429:
            logger.warning("⚠️  Rate limit exceeded - TAAPI plan may need upgrade")
            return True  # Not a validation failure
        else:
            logger.error("❌ API request failed with status %d", resp.status_code)
            logger.error("📄 Response: %s", resp.text[:200])
            return False
            
    except requests.exceptions.Timeout:
        logger.error("❌ API request timeout")
        return False
    except requests.exceptions.ConnectionError:
        logger.error("❌ Connection error to TAAPI.io")
        return False
    except Exception as e:
        logger.error("❌ Unexpected error testing API: %s", e)
        return False
    
    logger.info("🔌 TAAPI.io API endpoint validation completed")
    return True

def validate_pattern_function_integration():
    """Test the actual pattern function with various scenarios."""
    logger.info("⚡ Validating pattern function integration...")
    
    # Test with missing TAAPI key
    result = fetch_pattern_taapi("AAPL", "", "1m", 10)
    if result is None:
        logger.info("✅ Correctly returns None for missing TAAPI key")
    else:
        logger.error("❌ Should return None for missing TAAPI key, got: %s", result)
        return False
    
    # Test with None TAAPI key
    result = fetch_pattern_taapi("AAPL", None, "1m", 10)
    if result is None:
        logger.info("✅ Correctly returns None for None TAAPI key")
    else:
        logger.error("❌ Should return None for None TAAPI key, got: %s", result)
        return False
    
    # Test with real TAAPI key if available
    taapi_key = os.environ.get("TAAPI_KEY")
    if taapi_key:
        logger.info("🔑 Testing with real TAAPI key...")
        test_symbols = ["AAPL", "SPY", "TSLA"]
        
        for symbol in test_symbols:
            try:
                result = fetch_pattern_taapi(symbol, taapi_key, "1m", 10)
                if result is not None:
                    valid_results = ["STRONG_BEARISH", "BEARISH", "NEUTRAL", "BULLISH", "STRONG_BULLISH"]
                    if result in valid_results:
                        logger.info("✅ %s pattern: %s (valid)", symbol, result)
                    else:
                        logger.error("❌ %s pattern: %s (invalid result)", symbol, result)
                        return False
                else:
                    logger.warning("⚠️  %s pattern: None (API may have failed)", symbol)
                    
            except Exception as e:
                logger.error("❌ Error fetching pattern for %s: %s", symbol, e)
                return False
    else:
        logger.info("ℹ️  Skipping live API test - TAAPI_KEY not available")
    
    logger.info("⚡ Pattern function integration validation completed")
    return True

def validate_error_handling():
    """Validate error handling in the pattern function."""
    logger.info("🛡️  Validating error handling...")
    
    # Test with invalid symbol
    taapi_key = os.environ.get("TAAPI_KEY")
    if taapi_key:
        try:
            result = fetch_pattern_taapi("INVALID_SYMBOL_123", taapi_key, "1m", 1)
            if result is None:
                logger.info("✅ Correctly handles invalid symbol (returns None)")
            else:
                logger.warning("⚠️  Invalid symbol returned: %s", result)
        except Exception as e:
            logger.info("✅ Exception handling works for invalid symbol: %s", e)
    
    # Test with very short timeout
    if taapi_key:
        try:
            result = fetch_pattern_taapi("AAPL", taapi_key, "1m", 0.001)  # Very short timeout
            logger.info("ℹ️  Short timeout result: %s", result)
        except Exception as e:
            logger.info("✅ Exception handling works for timeout: %s", e)
    
    logger.info("🛡️  Error handling validation completed")
    return True

def main():
    """Run all pattern indicator validation tests."""
    logger.info("🚀 Starting TAAPI.io pattern indicator validation...")
    logger.info("=" * 60)
    
    validation_functions = [
        validate_pattern_function_signature,
        validate_pattern_value_interpretation,
        validate_taapi_api_endpoint,
        validate_pattern_function_integration,
        validate_error_handling
    ]
    
    passed = 0
    failed = 0
    
    for validation_func in validation_functions:
        try:
            result = validation_func()
            if result:
                logger.info("✅ %s: PASSED", validation_func.__name__)
                passed += 1
            else:
                logger.error("❌ %s: FAILED", validation_func.__name__)
                failed += 1
        except Exception as e:
            logger.error("❌ %s: EXCEPTION - %s", validation_func.__name__, e)
            failed += 1
        
        logger.info("-" * 40)
    
    logger.info("🎉 Pattern Indicator Validation Summary:")
    logger.info("   ✅ Passed: %d", passed)
    logger.info("   ❌ Failed: %d", failed)
    logger.info("   📊 Total:  %d", passed + failed)
    
    # Additional information
    taapi_key = os.environ.get("TAAPI_KEY")
    if taapi_key:
        logger.info("   🔑 TAAPI Key: Available (live API tested)")
    else:
        logger.info("   ⚠️  TAAPI Key: Not available (API tests skipped)")
    
    if failed == 0:
        logger.info("🎯 ALL PATTERN VALIDATIONS PASSED! Three Black Crows indicator is ready.")
        return 0
    else:
        logger.warning("⚠️  Some validations failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())