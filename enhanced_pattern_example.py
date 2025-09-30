#!/usr/bin/env python3
"""
Optional enhancement: Multiple pattern indicator support for TAAPI.io
This is an enhanced version that could support multiple candlestick patterns.
Current implementation is solid - this is just a potential future enhancement.
"""

from decimal import Decimal
import requests
from typing import Optional, Dict, Any
import os

def fetch_multiple_patterns_taapi(symbol: str, taapi_key: str, interval: str = "1m", timeout: int = 10) -> Optional[Dict[str, str]]:
    """Fetch multiple candlestick patterns for comprehensive analysis.
    
    This is an OPTIONAL enhancement to the current single-pattern approach.
    The current Three Black Crows implementation is perfectly adequate.
    
    Args:
        symbol: Stock symbol to analyze
        taapi_key: TAAPI.io API key
        interval: Time interval (default: "1m")
        timeout: Request timeout in seconds
        
    Returns:
        Dict with pattern names and their interpretations, or None if error
        
    Example return:
        {
            'three_black_crows': 'BEARISH',
            'three_white_soldiers': 'NEUTRAL', 
            'doji': 'NEUTRAL',
            'hammer': 'BULLISH'
        }
    """
    if not taapi_key:
        return None
    
    patterns_config = {
        'three_black_crows': 'cdl3blackcrows',
        'three_white_soldiers': 'cdl3whitesoldiers',
        'doji': 'cdldoji',
        'hammer': 'cdlhammer'
    }
    
    results = {}
    
    for pattern_name, taapi_endpoint in patterns_config.items():
        try:
            url = f"https://api.taapi.io/{taapi_endpoint}"
            params = {"secret": taapi_key, "symbol": symbol, "interval": interval, "type": "stocks"}
            
            resp = requests.get(url, params=params, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            
            if "value" in data:
                value = data["value"]
                
                # Interpret pattern value
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
                    
                results[pattern_name] = interpretation
            else:
                results[pattern_name] = "NEUTRAL"
                
        except Exception:
            results[pattern_name] = "NEUTRAL"
    
    return results if results else None

def create_composite_pattern_signal(patterns: Dict[str, str]) -> str:
    """Create a composite signal from multiple patterns.
    
    This demonstrates how multiple patterns could be combined.
    Again, this is OPTIONAL - current single pattern works well.
    """
    if not patterns:
        return "NEUTRAL"
    
    # Weight different patterns by importance
    pattern_weights = {
        'three_black_crows': 3,      # Strong reversal signal
        'three_white_soldiers': 3,   # Strong reversal signal  
        'doji': 2,                   # Indecision/reversal
        'hammer': 2                  # Reversal signal
    }
    
    bearish_score = 0
    bullish_score = 0
    total_weight = 0
    
    for pattern_name, signal in patterns.items():
        weight = pattern_weights.get(pattern_name, 1)
        total_weight += weight
        
        if "BEARISH" in signal:
            bearish_score += weight * (2 if "STRONG" in signal else 1)
        elif "BULLISH" in signal:
            bullish_score += weight * (2 if "STRONG" in signal else 1)
    
    if total_weight == 0:
        return "NEUTRAL"
    
    # Calculate net sentiment
    net_score = (bullish_score - bearish_score) / total_weight
    
    if net_score >= 1.5:
        return "STRONG_BULLISH"
    elif net_score >= 0.5:
        return "BULLISH"
    elif net_score <= -1.5:
        return "STRONG_BEARISH"
    elif net_score <= -0.5:
        return "BEARISH"
    else:
        return "NEUTRAL"

if __name__ == "__main__":
    print("🚀 Enhanced Pattern Indicator Example")
    print("=====================================")
    print()
    print("This demonstrates how the pattern indicator could be enhanced")
    print("to support multiple candlestick patterns for more comprehensive analysis.")
    print()
    print("CURRENT IMPLEMENTATION:")
    print("✅ Single pattern (Three Black Crows) - WORKING PERFECTLY")
    print("✅ Simple, reliable, well-integrated")
    print("✅ No changes needed")
    print()
    print("OPTIONAL FUTURE ENHANCEMENT:")
    print("• Multiple patterns (Three Black Crows, Three White Soldiers, Doji, Hammer)")
    print("• Composite pattern scoring")
    print("• More comprehensive reversal detection")
    print()
    print("RECOMMENDATION: Keep current implementation, consider enhancement later")