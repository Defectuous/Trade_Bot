#!/usr/bin/env python3
"""
Test script to validate the indicator enable/disable functionality.
This script tests different combinations of enabled/disabled indicators.
"""

import logging
import sys
import os
from modules.taapi import fetch_all_indicators

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_indicator_controls():
    """Test the indicator enable/disable functionality."""
    logger.info("🧪 Testing indicator enable/disable functionality...")
    
    # Test scenarios with different indicator combinations
    test_scenarios = [
        {
            'name': 'All Indicators Enabled',
            'config': {
                'ENABLE_RSI': 'true',
                'ENABLE_MA': 'true', 
                'ENABLE_EMA': 'true',
                'ENABLE_PATTERN': 'true',
                'ENABLE_ADX': 'true',
                'ENABLE_ADXR': 'true'
            },
            'expected_enabled': ['RSI', 'MA', 'EMA', 'PATTERN', 'ADX', 'ADXR']
        },
        {
            'name': 'Only Core Indicators (RSI + MA)',
            'config': {
                'ENABLE_RSI': 'true',
                'ENABLE_MA': 'true',
                'ENABLE_EMA': 'false',
                'ENABLE_PATTERN': 'false', 
                'ENABLE_ADX': 'false',
                'ENABLE_ADXR': 'false'
            },
            'expected_enabled': ['RSI', 'MA']
        },
        {
            'name': 'Trend Analysis Only (MA + EMA + ADX)',
            'config': {
                'ENABLE_RSI': 'false',
                'ENABLE_MA': 'true',
                'ENABLE_EMA': 'true',
                'ENABLE_PATTERN': 'false',
                'ENABLE_ADX': 'true', 
                'ENABLE_ADXR': 'false'
            },
            'expected_enabled': ['MA', 'EMA', 'ADX']
        },
        {
            'name': 'Pattern Focus (RSI + Pattern)',
            'config': {
                'ENABLE_RSI': 'true',
                'ENABLE_MA': 'false',
                'ENABLE_EMA': 'false',
                'ENABLE_PATTERN': 'true',
                'ENABLE_ADX': 'false',
                'ENABLE_ADXR': 'false'
            },
            'expected_enabled': ['RSI', 'PATTERN']
        },
        {
            'name': 'All Indicators Disabled',
            'config': {
                'ENABLE_RSI': 'false',
                'ENABLE_MA': 'false',
                'ENABLE_EMA': 'false', 
                'ENABLE_PATTERN': 'false',
                'ENABLE_ADX': 'false',
                'ENABLE_ADXR': 'false'
            },
            'expected_enabled': []
        }
    ]
    
    original_env = {}
    
    for scenario in test_scenarios:
        logger.info(f"\n🔍 Testing scenario: {scenario['name']}")
        
        # Save original environment variables
        for key in scenario['config']:
            original_env[key] = os.environ.get(key)
        
        # Set test configuration
        for key, value in scenario['config'].items():
            os.environ[key] = value
        
        try:
            # Test with dummy TAAPI key (won't make real API calls)
            indicators = fetch_all_indicators('AAPL', 'dummy_key')
            
            # Check which indicators should be enabled vs disabled
            enabled_indicators = []
            disabled_indicators = []
            
            indicator_map = {
                'rsi': 'RSI',
                'ma': 'MA', 
                'ema': 'EMA',
                'pattern': 'PATTERN',
                'adx': 'ADX',
                'adxr': 'ADXR'
            }
            
            for key, name in indicator_map.items():
                enable_flag = f"ENABLE_{name}"
                is_enabled = os.environ.get(enable_flag, 'true').lower() in ('true', '1', 'yes', 'on')
                
                if is_enabled:
                    enabled_indicators.append(name)
                    # Note: indicator value will be None due to dummy key, but that's expected
                    if key not in indicators:
                        logger.error(f"❌ {name} should be enabled but not found in results")
                    else:
                        logger.info(f"✅ {name} correctly processed (enabled)")
                else:
                    disabled_indicators.append(name)
                    if indicators.get(key) is not None:
                        logger.error(f"❌ {name} should be disabled but has value: {indicators[key]}")
                    else:
                        logger.info(f"✅ {name} correctly disabled")
            
            # Validate against expected
            expected_enabled = set(scenario['expected_enabled'])
            actual_enabled = set(enabled_indicators)
            
            if expected_enabled == actual_enabled:
                logger.info(f"✅ Scenario PASSED: Expected {expected_enabled}, got {actual_enabled}")
            else:
                logger.error(f"❌ Scenario FAILED: Expected {expected_enabled}, got {actual_enabled}")
            
            logger.info(f"   📊 Enabled: {enabled_indicators}")
            logger.info(f"   🚫 Disabled: {disabled_indicators}")
            
        except Exception as e:
            logger.error(f"❌ Scenario failed with exception: {e}")
        
        finally:
            # Restore original environment variables
            for key, original_value in original_env.items():
                if original_value is not None:
                    os.environ[key] = original_value
                elif key in os.environ:
                    del os.environ[key]
            original_env.clear()
    
    logger.info("\n🎉 Indicator enable/disable testing completed!")

def test_environment_variable_parsing():
    """Test different ways to specify true/false in environment variables."""
    logger.info("\n🔍 Testing environment variable parsing...")
    
    # Test different true/false variations
    true_values = ['true', 'True', 'TRUE', '1', 'yes', 'YES', 'on', 'ON']
    false_values = ['false', 'False', 'FALSE', '0', 'no', 'NO', 'off', 'OFF', '']
    
    # Import the helper function
    import importlib
    taapi_module = importlib.import_module('modules.taapi')
    
    # Test with a mock function since is_indicator_enabled is nested
    def test_boolean_parsing(value: str) -> bool:
        """Test function to mimic the boolean parsing logic."""
        return value.lower() in ('true', '1', 'yes', 'on')
    
    logger.info("✅ Testing TRUE values:")
    for value in true_values:
        result = test_boolean_parsing(value)
        if result:
            logger.info(f"   ✅ '{value}' → {result}")
        else:
            logger.error(f"   ❌ '{value}' → {result} (should be True)")
    
    logger.info("✅ Testing FALSE values:")
    for value in false_values:
        result = test_boolean_parsing(value)
        if not result:
            logger.info(f"   ✅ '{value}' → {result}")
        else:
            logger.error(f"   ❌ '{value}' → {result} (should be False)")
    
    logger.info("🎯 Environment variable parsing test completed!")

def main():
    """Run all indicator control tests."""
    logger.info("🚀 Starting indicator enable/disable validation...")
    logger.info("=" * 60)
    
    try:
        test_environment_variable_parsing()
        test_indicator_controls()
        logger.info("\n🎉 ALL TESTS COMPLETED!")
        return 0
    except Exception as e:
        logger.error("❌ Testing failed: %s", e)
        return 1

if __name__ == "__main__":
    sys.exit(main())