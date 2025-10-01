"""Alpaca helper utilities.

Small, well-documented helpers to connect to Alpaca and fetch common data.
These functions are defensive and return Decimal where appropriate.
"""
from decimal import Decimal
import logging
import os
import time
from typing import Dict, Optional

logger = logging.getLogger(__name__)

try:
    import alpaca_trade_api as tradeapi
except Exception:
    tradeapi = None


def connect_alpaca(api_key: Optional[str] = None, secret_key: Optional[str] = None, base_url: Optional[str] = None):
    """Connect to Alpaca API and return REST client instance.
    
    Args:
        api_key: Alpaca API key (defaults to ALPACA_API_KEY env var)
        secret_key: Alpaca secret key (defaults to ALPACA_SECRET_KEY env var)  
        base_url: Alpaca base URL (defaults to ALPACA_BASE_URL env var or paper trading)
        
    Returns:
        Alpaca REST API client instance
        
    Raises:
        RuntimeError: If credentials not provided or SDK not installed
    """
    api_key = api_key or os.environ.get("ALPACA_API_KEY")
    secret_key = secret_key or os.environ.get("ALPACA_SECRET_KEY")
    base_url = base_url or os.environ.get("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
    if not api_key or not secret_key:
        raise RuntimeError("Alpaca credentials not set")
    if tradeapi is None:
        raise RuntimeError("alpaca_trade_api package not installed")
    base = base_url.split()[0].strip().rstrip('/')
    logger.info("Connecting to Alpaca at %s", base)
    return tradeapi.REST(api_key, secret_key, base_url=base)


def _retry_alpaca_call(func, max_retries=None, delay=None, backoff=None):
    """Retry wrapper for Alpaca API calls with exponential backoff."""
    # Use environment variables or defaults
    if max_retries is None:
        max_retries = int(os.environ.get("ALPACA_RETRY_ATTEMPTS", "3"))
    if delay is None:
        delay = float(os.environ.get("ALPACA_RETRY_DELAY", "2"))
    if backoff is None:
        backoff = float(os.environ.get("ALPACA_RETRY_BACKOFF", "2"))
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                # Last attempt, re-raise the exception
                logger.error("Alpaca API call failed after %d attempts: %s", max_retries, str(e))
                raise
            
            # Enhanced error detection for different exception types
            should_retry = False
            status_code = None
            
            # Check for HTTPError from requests library (most common)
            if hasattr(e, 'response') and e.response is not None:
                status_code = getattr(e.response, 'status_code', None)
                if status_code is not None and 500 <= status_code <= 599:
                    should_retry = True
            
            # Check for Alpaca SDK specific exceptions that might contain status codes
            elif 'Server Error' in str(e) or '500' in str(e) or '502' in str(e) or '503' in str(e) or '504' in str(e):
                should_retry = True
                # Try to extract status code from error message
                error_str = str(e)
                if '500' in error_str:
                    status_code = 500
                elif '502' in error_str:
                    status_code = 502
                elif '503' in error_str:
                    status_code = 503
                elif '504' in error_str:
                    status_code = 504
                else:
                    status_code = 500  # Default to 500 for server errors
            
            # Check for network-related errors that should be retried
            elif any(keyword in str(e).lower() for keyword in ['connection', 'timeout', 'network', 'unreachable']):
                should_retry = True
                status_code = 'Network'
            
            if should_retry:
                wait_time = delay * (backoff ** attempt)
                if isinstance(status_code, int):
                    logger.warning("Alpaca server error (HTTP %d), retrying in %.1f seconds (attempt %d/%d): %s", 
                                 status_code, wait_time, attempt + 1, max_retries, str(e))
                else:
                    logger.warning("Alpaca %s error, retrying in %.1f seconds (attempt %d/%d): %s", 
                                 status_code, wait_time, attempt + 1, max_retries, str(e))
                time.sleep(wait_time)
                continue
            else:
                # Non-retryable error
                if status_code:
                    logger.error("Alpaca API error (HTTP %d), not retrying: %s", status_code, str(e))
                else:
                    logger.error("Alpaca API error, not retrying: %s", str(e))
                raise


def get_wallet_amount(api, field: str = "cash") -> Decimal:
    """Return the requested numeric field from the Alpaca account as Decimal.

    Common fields: cash, buying_power, portfolio_value, equity
    """
    def _get_account():
        return api.get_account()
    
    try:
        acct = _retry_alpaca_call(_get_account)
        val = getattr(acct, field, None)
        if val is None:
            # some SDKs return dict-like
            try:
                val = acct[field]
            except Exception:
                raise
        return Decimal(str(val))
    except Exception:
        logger.exception("Failed to fetch Alpaca account: %s", field)
        raise


def get_owned_positions(api) -> Dict[str, Decimal]:
    """Return a dict mapping symbol -> Decimal(quantity) for all owned positions."""
    def _get_positions():
        try:
            return api.list_positions()
        except Exception:
            # Older SDKs used get_positions
            return api.get_positions()
    
    out = {}
    try:
        positions = _retry_alpaca_call(_get_positions)
    except Exception:
        logger.exception("Failed to fetch positions")
        raise
        
    for p in positions:
        # SDK may return objects or dicts
        if isinstance(p, dict):
            symbol = p.get('symbol')
            qty = p.get('qty')
        else:
            symbol = getattr(p, 'symbol', None)
            qty = getattr(p, 'qty', None)
        if symbol is None or qty is None:
            continue
        try:
            out[symbol] = Decimal(str(qty))
        except Exception:
            try:
                out[symbol] = Decimal(qty)
            except Exception:
                logger.debug("Skipping position with unparsable qty: %s %s", symbol, qty)
    return out


def get_last_trade_price(api, symbol: str) -> Decimal:
    """Return last trade price as Decimal for symbol."""
    def _get_latest_quote():
        # Try the modern quote endpoint first
        quote = api.get_latest_quote(symbol)
        if hasattr(quote, 'ask_price') and hasattr(quote, 'bid_price'):
            # Use mid-price between bid and ask
            ask = Decimal(str(quote.ask_price))
            bid = Decimal(str(quote.bid_price))
            return (ask + bid) / 2
        elif hasattr(quote, 'price'):
            return Decimal(str(quote.price))
        else:
            raise ValueError(f"Could not extract price from quote for {symbol}")
    
    def _get_latest_bar():
        # Try the modern bars endpoint as fallback
        bars = api.get_bars(symbol, '1Min', limit=1)
        if bars and len(bars) > 0:
            latest_bar = bars[-1]
            # Use closing price from the latest bar
            if hasattr(latest_bar, 'c'):
                return Decimal(str(latest_bar.c))
            elif hasattr(latest_bar, 'close'):
                return Decimal(str(latest_bar.close))
            else:
                raise ValueError(f"Could not extract close price from bar for {symbol}")
        else:
            raise ValueError(f"No bar data available for {symbol}")
    
    def _get_snapshot():
        # Try snapshot endpoint as another fallback
        snapshot = api.get_snapshot(symbol)
        if hasattr(snapshot, 'latest_trade') and snapshot.latest_trade:
            return Decimal(str(snapshot.latest_trade.price))
        elif hasattr(snapshot, 'latest_quote') and snapshot.latest_quote:
            # Use mid-price from quote
            ask = Decimal(str(snapshot.latest_quote.ask_price))
            bid = Decimal(str(snapshot.latest_quote.bid_price))
            return (ask + bid) / 2
        else:
            raise ValueError(f"Could not extract price from snapshot for {symbol}")
    
    # Try different methods in order of preference
    for method_name, method_func in [
        ("latest_quote", _get_latest_quote),
        ("latest_bar", _get_latest_bar), 
        ("snapshot", _get_snapshot)
    ]:
        try:
            price = _retry_alpaca_call(method_func)
            logger.debug("Successfully got price for %s using %s: %s", symbol, method_name, price)
            return price
        except Exception as e:
            logger.debug("Failed to get price for %s using %s: %s", symbol, method_name, str(e))
            continue
    
    # If all methods fail, raise an exception
    logger.exception("Failed to fetch last trade price for %s using all available methods", symbol)
    raise RuntimeError(f"Could not fetch price for {symbol} - all price endpoints failed")


def place_order(api, symbol: str, qty, side: str = 'buy'):
    """Place a market order. Supports both whole shares (int) and fractional shares (float).
    
    Args:
        api: Alpaca REST client instance
        symbol: Stock symbol to trade
        qty: Quantity to trade - can be int (whole shares) or float (fractional shares)
        side: 'buy' or 'sell'
        
    Returns:
        Order object from Alpaca API
        
    Note:
        Alpaca supports fractional shares for most stocks. The API automatically
        handles fractional quantities when a float is provided.
    """
    def _submit_order():
        # Alpaca API accepts both int and float quantities
        # Float values enable fractional share trading
        return api.submit_order(symbol=symbol, qty=qty, side=side, type='market', time_in_force='day')
    
    # Log the order type for clarity
    order_type = "fractional" if isinstance(qty, float) and qty != int(qty) else "whole"
    logger.info("Submitting %s share %s order: %s %s", order_type, side.upper(), qty, symbol)
    
    try:
        return _retry_alpaca_call(_submit_order)
    except Exception:
        logger.exception("Order submission failed: %s %s %s", side, qty, symbol)
        raise


def can_buy(api, price: Decimal, qty) -> bool:
    """Return True if buying `qty` shares at `price` is allowed by buying power.
    
    Args:
        api: Alpaca REST client instance
        price: Price per share as Decimal
        qty: Quantity to buy - can be int (whole shares) or float (fractional shares)
        
    Returns:
        True if purchase is within buying power limits, False otherwise
    """
    try:
        # Get buying power
        bp = get_wallet_amount(api, 'buying_power')
        
        # Calculate total cost needed
        needed = price * Decimal(str(qty))
        
        # Add small buffer for fees/slippage (0.5%)
        needed_with_buffer = needed * Decimal("1.005")
        
        # Log the check for transparency
        logger.debug("Fund check: Need $%s (with buffer: $%s), have $%s buying power", 
                    needed, needed_with_buffer, bp)
        
        # Ensure we have enough buying power with buffer
        can_afford = bp >= needed_with_buffer
        
        if not can_afford:
            logger.warning("Insufficient buying power: Need $%s, have $%s (deficit: $%s)", 
                         needed_with_buffer, bp, needed_with_buffer - bp)
        
        return can_afford
        
    except Exception as e:
        logger.exception("can_buy check failed: %s", e)
        return False  # Default to safe (don't buy) if check fails


def is_fractionable(api, symbol: str) -> bool:
    """Check if an asset supports fractional trading.
    
    Args:
        api: Alpaca REST client instance
        symbol: Stock symbol to check
        
    Returns:
        True if asset supports fractional shares, False otherwise
        
    Note:
        Returns False if asset info cannot be retrieved (safer default)
    """
    try:
        # Get asset information
        asset = api.get_asset(symbol)
        
        # Check if asset is fractionable
        fractionable = getattr(asset, 'fractionable', False)
        logger.debug("Asset %s fractionable status: %s", symbol, fractionable)
        
        return fractionable
        
    except Exception as e:
        logger.warning("Could not check fractionable status for %s: %s", symbol, e)
        return False  # Default to whole shares only if check fails


def owns_at_least(api, symbol: str, qty) -> bool:
    """Check if account owns at least the specified quantity of a symbol.
    
    Args:
        api: Alpaca REST client instance
        symbol: Stock symbol to check
        qty: Minimum quantity to check for - can be int or float for fractional shares
        
    Returns:
        True if account owns at least qty shares of symbol, False otherwise
        
    Note:
        Returns False if position cannot be retrieved (assumes 0 shares)
        Supports fractional share comparisons
    """
    def _get_position():
        return api.get_position(symbol)
    
    try:
        p = _retry_alpaca_call(_get_position)
        q = getattr(p, 'qty', None)
        if q is None:
            try:
                q = p['qty']
            except Exception:
                return False
        return Decimal(str(q)) >= Decimal(str(qty))  # Support fractional comparisons
    except Exception:
        logger.debug("Could not check position for %s: assuming 0", symbol)
        return False
