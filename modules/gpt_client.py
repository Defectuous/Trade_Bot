"""GPT client wrapper (OpenAI).

Provides functions to ask trading decision questions using comprehensive technical analysis.
Enhanced version supports 6 technical indicators: RSI, MA, EMA, Three Black Crows, ADX, ADXR.
Logs prompt and raw reply for auditing. Designed to be resilient to OpenAI client differences.
"""
from decimal import Decimal
import logging
from typing import Tuple, Optional, Dict, Any

logger = logging.getLogger(__name__)

try:
    import openai
except Exception:
    openai = None


def ask_gpt_for_decision(openai_api_key: str, model: str, indicators: Dict[str, Any], symbol: str, shares_owned: Decimal, stock_price: Decimal, wallet: Decimal) -> Tuple[str, Optional[Decimal]]:
    """Ask GPT for a decision using comprehensive technical analysis.
    
    Enhanced version that uses 6 technical indicators for more sophisticated trading decisions.
    
    Args:
        openai_api_key: OpenAI API key
        model: GPT model to use (e.g., "gpt-3.5-turbo")
        indicators: Dict containing all technical indicators (RSI, MA, EMA, Pattern, ADX, ADXR)
        symbol: Stock symbol being analyzed
        shares_owned: Current shares owned of this stock
        stock_price: Current stock price
        wallet: Available cash balance
    
    Returns:
        Tuple of (action, amount) where action is 'BUY', 'SELL', or 'NOTHING'
    """
    if not openai_api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    if openai is None:
        raise RuntimeError("openai package not installed")

    Client = getattr(openai, "OpenAI", None)
    if Client is None:
        raise RuntimeError("openai package does not expose OpenAI client; please install openai>=1.0.0")

    # Extract indicator values and filter out invalid ones
    valid_indicators = []
    indicator_definitions = {
        'rsi': {'value': indicators.get('rsi'), 'desc': 'RSI (Relative Strength Index)', 'guide': '[Overbought >70, Oversold <30]'},
        'ma': {'value': indicators.get('ma'), 'desc': 'MA (Moving Average)', 'guide': '[Price vs MA indicates trend direction]'},
        'ema': {'value': indicators.get('ema'), 'desc': 'EMA (Exponential Moving Average)', 'guide': '[More responsive to recent price changes]'},
        'pattern': {'value': indicators.get('pattern'), 'desc': 'Pattern Analysis (Three Black Crows)', 'guide': '[STRONG_BEARISH/BEARISH/NEUTRAL/BULLISH/STRONG_BULLISH]'},
        'adx': {'value': indicators.get('adx'), 'desc': 'ADX (Average Directional Index)', 'guide': '[Trend strength: >25 strong, <20 weak]'},
        'adxr': {'value': indicators.get('adxr'), 'desc': 'ADXR (Average Directional Index Rating)', 'guide': '[Trend stability indicator]'}
    }
    
    # Build list of valid indicators (not None, not 'N/A', not empty)
    for indicator_name, indicator_info in indicator_definitions.items():
        value = indicator_info['value']
        if value is not None and value != 'N/A' and str(value).strip():
            valid_indicators.append(f"• {indicator_info['desc']}: {value} {indicator_info['guide']}")
    
    # Ensure we have at least one indicator
    if not valid_indicators:
        # Fallback to basic prompt without technical indicators
        prompt = (
            f"You are an expert stock trader specializing in day trading. "
            f"Analyze {symbol} using basic market data only (technical indicators unavailable):\n\n"
            f"POSITION & FINANCIAL DATA:\n"
            f"• Current Stock Price: ${stock_price}\n"
            f"• Shares Currently Owned: {shares_owned}\n"
            f"• Available Cash: ${wallet}\n\n"
            f"TRADING RULES:\n"
            f"• ABSOLUTE MAXIMUM: ${wallet} (your total available cash)\n"
            f"• Recommended trade size: 2% of wallet = ${wallet * Decimal('0.02'):.2f}\n"
            f"• For accounts <$500: Use $10-$50 maximum per trade\n"
            f"• NEVER recommend amounts exceeding available cash\n"
            f"• Consider current position and market conditions\n\n"
            f"Based on basic market analysis, provide your trading decision.\n"
            f"IMPORTANT: With ${wallet} available, your BUY amount MUST be ≤ ${wallet}.\n"
            f"Reply EXACTLY in this format: BUY $[Amount ≤ {wallet}], SELL [Shares], or NOTHING\n"
            f"Examples for your ${wallet} budget: BUY $20, BUY $50, BUY ${min(wallet, 100):.0f}, NOTHING"
        )
        logger.warning("No valid technical indicators available for %s, using basic prompt", symbol)
    else:
        # Dynamic prompt with only valid indicators
        indicators_text = "\n".join(valid_indicators)
        
        # Build trading guidelines based on available indicators
        trading_guidelines = []
        if any('RSI' in ind for ind in valid_indicators):
            trading_guidelines.append("• RSI for momentum and overbought/oversold conditions")
        if any('MA' in ind or 'EMA' in ind for ind in valid_indicators):
            trading_guidelines.append("• Price position relative to MA/EMA for trend confirmation")
        if any('ADX' in ind for ind in valid_indicators):
            trading_guidelines.append("• Consider trend strength (ADX) and pattern analysis together")
        if any('Pattern' in ind for ind in valid_indicators):
            trading_guidelines.append("• Pattern analysis for reversal signals")
        
        # Default guideline if no specific ones apply
        if not trading_guidelines:
            trading_guidelines.append("• Use confluence of available indicators for stronger signals")
        
        # Add wallet-specific guidelines for small accounts
        if wallet < 500:
            trading_guidelines.append(f"• 🚨 CRITICAL: SMALL ACCOUNT (${wallet}) - Maximum trade: ${min(wallet * Decimal('0.5'), 50):.0f}")
            trading_guidelines.append(f"• REQUIRED: Dollar amount MUST be ≤ ${wallet}")
            trading_guidelines.append(f"• Suggested range: $10-$50 for safety")
        elif wallet < 1000:
            trading_guidelines.append(f"• CONSERVATIVE ACCOUNT: ${wallet} available - max ${wallet * Decimal('0.7'):.0f} per trade")
            trading_guidelines.append(f"• REQUIRED: Dollar amount MUST be ≤ ${wallet}")
            
        guidelines_text = "\n".join(trading_guidelines)
        
        prompt = (
            f"You are an expert stock trader specializing in day trading with advanced technical analysis expertise. "
            f"Analyze {symbol} using the following available technical indicators:\n\n"
            f"TECHNICAL INDICATORS:\n"
            f"{indicators_text}\n\n"
            f"POSITION & FINANCIAL DATA:\n"
            f"• Current Stock Price: ${stock_price}\n"
            f"• Shares Currently Owned: {shares_owned}\n"
            f"• Available Cash: ${wallet}\n\n"
            f"TRADING RULES:\n"
            f"• ABSOLUTE MAXIMUM: ${wallet} (your total available cash)\n"
            f"• Recommended trade size: 2% of wallet = ${wallet * Decimal('0.02'):.2f}\n"
            f"• For accounts <$500: Use $10-$50 maximum per trade\n"
            f"• NEVER recommend amounts exceeding available cash\n"
            f"{guidelines_text}\n\n"
            f"Based on the available technical analysis, provide your trading decision.\n"
            f"IMPORTANT: With ${wallet} available, your BUY amount MUST be ≤ ${wallet}.\n"
            f"Reply EXACTLY in this format: BUY $[Amount ≤ {wallet}], SELL [Shares], or NOTHING\n"
            f"Examples for your ${wallet} budget: BUY $20, BUY $50, BUY ${min(wallet, 100):.0f}, NOTHING"
        )
        
        logger.info("Using %d valid indicators for %s: %s", 
                   len(valid_indicators), symbol, 
                   [ind.split(':')[0].replace('•', '').strip() for ind in valid_indicators])

    logger.debug("Enhanced GPT prompt: %s", prompt)

    client = Client(api_key=openai_api_key)

    # Adjust temperature for small accounts - be more conservative
    temperature = 0 if wallet >= 500 else 0
    max_tokens = 60 if wallet < 500 else 50  # Slightly more tokens for detailed small account responses

    text = None
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        try:
            text = resp.choices[0].message.content.strip()
        except Exception:
            try:
                text = resp["choices"][0]["message"]["content"].strip()
            except Exception:
                text = str(resp).strip()
    except Exception as e:
        logger.debug("Chat completions call failed: %s", e)
        # try legacy completions
        try:
            resp2 = client.completions.create(model=model, prompt=prompt, max_tokens=50, temperature=0)
            try:
                text = resp2.choices[0].text.strip()
            except Exception:
                text = str(resp2).strip()
        except Exception:
            logger.exception("GPT API call failed")
            raise

    logger.info("Enhanced GPT raw reply: %s", text)

    if not text:
        return "NOTHING", None

    parts = text.strip().split()
    if not parts:
        return "NOTHING", None
    action = parts[0].upper()
    amount = None
    if action not in ("BUY", "SELL", "NOTHING"):
        return "NOTHING", None
    if action in ("BUY", "SELL") and len(parts) >= 2:
        try:
            # Handle dollar amounts for BUY orders (e.g., "BUY $5000")
            raw_amount = parts[1]
            if raw_amount.startswith('$'):
                # Dollar amount - convert to shares based on current stock price
                dollar_str = raw_amount[1:].replace(',', '')  # Remove $ and commas
                dollar_amount = Decimal(dollar_str)
                
                # Validate GPT recommendation against wallet
                if action == "BUY" and dollar_amount > wallet:
                    logger.warning("🚨 GPT OVER-RECOMMENDATION: Suggested $%s but only $%s available. GPT prompt may need improvement.", 
                                 dollar_amount, wallet)
                
                if stock_price > 0:
                    amount = dollar_amount / stock_price  # Convert to shares
                    logger.info("Converted dollar amount $%s to %s shares at $%s per share", 
                               dollar_amount, amount, stock_price)
                else:
                    logger.warning("Cannot convert dollar amount - invalid stock price: %s", stock_price)
                    amount = None
            else:
                # Direct number (shares for SELL, or legacy format)
                amount = Decimal(raw_amount.replace(',', ''))  # Remove commas if present
        except Exception:
            # Fallback parsing for malformed responses
            cleaned = ''.join(c for c in parts[1] if (c.isdigit() or c in '.-$,'))
            try:
                if cleaned.startswith('$'):
                    # Dollar amount parsing fallback
                    dollar_str = cleaned[1:].replace(',', '')
                    dollar_amount = Decimal(dollar_str)
                    
                    # Validate fallback parsing too
                    if action == "BUY" and dollar_amount > wallet:
                        logger.warning("🚨 GPT OVER-RECOMMENDATION (fallback): Suggested $%s but only $%s available", 
                                     dollar_amount, wallet)
                    
                    if stock_price > 0:
                        amount = dollar_amount / stock_price
                        logger.info("Fallback: Converted dollar amount $%s to %s shares", 
                                   dollar_amount, amount)
                    else:
                        amount = None
                else:
                    cleaned_no_commas = cleaned.replace(',', '')
                    amount = Decimal(cleaned_no_commas) if cleaned_no_commas else None
            except Exception:
                amount = None

    return action, amount


# Keep legacy function for backward compatibility
def ask_gpt_for_decision_legacy(openai_api_key: str, model: str, rsi_value: Decimal, symbol: str, shares_owned: Decimal, stock_price: Decimal, wallet: Decimal) -> Tuple[str, Optional[Decimal]]:
    """Legacy function for single RSI-based decisions. Use ask_gpt_for_decision for enhanced analysis."""
    indicators = {'rsi': rsi_value, 'ma': 'N/A', 'ema': 'N/A', 'pattern': 'N/A', 'adx': 'N/A', 'adxr': 'N/A'}
    return ask_gpt_for_decision(openai_api_key, model, indicators, symbol, shares_owned, stock_price, wallet)
