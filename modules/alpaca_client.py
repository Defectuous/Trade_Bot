"""Alpaca helper utilities.

Small, well-documented helpers to connect to Alpaca and fetch common data.
These functions are defensive and return Decimal where appropriate.
"""
from decimal import Decimal
import logging
import os
from typing import Dict, Optional

logger = logging.getLogger(__name__)

try:
    import alpaca_trade_api as tradeapi
except Exception:
    tradeapi = None


def connect_alpaca(api_key: Optional[str] = None, secret_key: Optional[str] = None, base_url: Optional[str] = None):
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


def get_wallet_amount(api, field: str = "cash") -> Decimal:
    """Return the requested numeric field from the Alpaca account as Decimal.

    Common fields: cash, buying_power, portfolio_value, equity
    """
    try:
        acct = api.get_account()
        val = getattr(acct, field, None)
        if val is None:
            # some SDKs return dict-like
            try:
                val = acct[field]
            except Exception:
                raise
        return Decimal(str(val))
    except Exception:
        logger.exception("Failed to fetch wallet amount")
        raise


def get_owned_positions(api) -> Dict[str, Decimal]:
    """Return a dict mapping symbol -> Decimal(quantity) for all owned positions."""
    out = {}
    try:
        positions = api.list_positions()
    except Exception:
        # Older SDKs used get_positions
        positions = api.get_positions()
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
    try:
        # Newer alpaca SDK exposes get_last_trade
        t = api.get_last_trade(symbol)
        price = getattr(t, 'price', None)
        if price is None:
            price = t['price']
        return Decimal(str(price))
    except Exception:
        # Fallback: try getting latest bar
        try:
            bars = api.get_barset(symbol, '1Min', limit=1)
            series = bars[symbol]
            if series:
                return Decimal(str(series[-1].c))
        except Exception:
            logger.exception("Failed to fetch last trade price for %s", symbol)
            raise


def place_order(api, symbol: str, qty: int, side: str = 'buy'):
    """Place a market order (qty must be int). Returns order object."""
    try:
        return api.submit_order(symbol=symbol, qty=qty, side=side, type='market', time_in_force='day')
    except Exception:
        logger.exception("Order submission failed: %s %s", side, symbol)
        raise


def can_buy(api, price: Decimal, qty: int) -> bool:
    """Return True if buying `qty` shares at `price` is allowed by buying power."""
    try:
        bp = get_wallet_amount(api, 'buying_power')
        needed = price * Decimal(qty)
        return bp >= needed
    except Exception:
        logger.exception("can_buy check failed")
        return False


def owns_at_least(api, symbol: str, qty: int) -> bool:
    try:
        p = api.get_position(symbol)
        q = getattr(p, 'qty', None)
        if q is None:
            try:
                q = p['qty']
            except Exception:
                return False
        return Decimal(str(q)) >= Decimal(qty)
    except Exception:
        return False
from decimal import Decimal
import os
import logging

logger = logging.getLogger(__name__)

try:
    import alpaca_trade_api as tradeapi
except Exception:
    tradeapi = None


def connect_alpaca(alpaca_key: Optional[str] = None, alpaca_secret: Optional[str] = None, base_url: Optional[str] = None):
    """Connect to Alpaca using provided credentials or environment variables.

    Args are optional; when not provided they are read from environment variables:
      - ALPACA_API_KEY
      - ALPACA_SECRET_KEY
      - ALPACA_BASE_URL (optional, defaults to paper trading URL)
    """
    # Prefer explicit args, then fall back to environment variables
    alpaca_key = alpaca_key or os.environ.get("ALPACA_API_KEY")
    alpaca_secret = alpaca_secret or os.environ.get("ALPACA_SECRET_KEY")
    base_url_raw = base_url or os.environ.get("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

    if not alpaca_key or not alpaca_secret:
        raise RuntimeError("Alpaca credentials not set")
    if tradeapi is None:
        raise RuntimeError("alpaca_trade_api package not installed")

    base = base_url_raw.split()[0].strip().rstrip('/')
    logger.info("Connecting to Alpaca at %s", base)
    return tradeapi.REST(alpaca_key, alpaca_secret, base_url=base)


def get_wallet_amount(api, field: str = "cash") -> Decimal:
    if api is None:
        raise RuntimeError("Alpaca API client is not provided")
    try:
        account = api.get_account()
    except Exception as e:
        logger.exception("Failed to fetch Alpaca account: %s", e)
        raise RuntimeError("Failed to fetch Alpaca account") from e
    normalized = field.strip().lower()
    candidates = [normalized, normalized.replace('-', '_')]
    alt_map = {
        "cash": ["cash", "cash_balance"],
        "buying_power": ["buying_power", "buyingpower"],
        "portfolio_value": ["portfolio_value", "portfoliovalue", "equity"],
        "equity": ["equity", "portfolio_value"],
    }
    if normalized in alt_map:
        candidates = alt_map[normalized] + candidates
    val = None
    for c in candidates:
        if hasattr(account, c):
            try:
                val = getattr(account, c)
                break
            except Exception:
                continue
    if val is None and isinstance(account, dict):
        for c in candidates:
            if c in account:
                val = account[c]
                break
    if val is None:
        for c in ("cash", "buying_power", "portfolio_value", "equity"):
            if hasattr(account, c):
                try:
                    val = getattr(account, c)
                    break
                except Exception:
                    continue
    if val is None:
        logger.error("Unable to find requested account field '%s' on Alpaca account object", field)
        raise RuntimeError(f"Account field '{field}' not found on Alpaca account")
    try:
        return Decimal(str(val))
    except Exception as e:
        logger.exception("Failed to convert account field '%s' value to Decimal: %s", field, e)
        raise RuntimeError(f"Invalid numeric value for account field '{field}'") from e


def get_owned_positions(api) -> dict:
    if api is None:
        raise RuntimeError("Alpaca API client is not provided")
    try:
        if hasattr(api, "list_positions"):
            positions = api.list_positions()
        elif hasattr(api, "get_positions"):
            positions = api.get_positions()
        elif hasattr(api, "get_all_positions"):
            positions = api.get_all_positions()
        else:
            raise RuntimeError("Alpaca client does not support listing positions")
    except Exception as e:
        logger.exception("Failed to list positions from Alpaca: %s", e)
        raise RuntimeError("Failed to list positions from Alpaca") from e
    owned = {}
    for p in positions:
        sym = None
        qty_val = None
        if isinstance(p, dict):
            sym = p.get("symbol") or p.get("ticker")
            qty_val = p.get("qty") or p.get("quantity") or p.get("shares")
        else:
            for a in ("symbol", "ticker"):
                if hasattr(p, a):
                    sym = getattr(p, a)
                    break
            for a in ("qty", "quantity", "shares"):
                if hasattr(p, a):
                    qty_val = getattr(p, a)
                    break
        if not sym:
            continue
        try:
            qty = Decimal(str(qty_val))
        except Exception:
            try:
                qty = Decimal(str(getattr(p, "qty", 0)))
            except Exception:
                qty = Decimal(0)
        owned[str(sym).upper()] = qty
    return owned


def get_last_trade_price(api, symbol: str) -> Decimal:
    try:
        if hasattr(api, "get_barset"):
            barset = api.get_barset(symbol, "1Min", limit=1)
            bars = barset.get(symbol)
            if bars:
                return Decimal(str(bars[-1].c))
    except Exception:
        pass
    for fn in ("get_last_trade", "get_latest_trade", "get_last_trades", "get_latest_trades"):
        if hasattr(api, fn):
            try:
                t = getattr(api, fn)(symbol)
                price = None
                if hasattr(t, "price"):
                    price = getattr(t, "price")
                elif isinstance(t, dict) and "price" in t:
                    price = t["price"]
                else:
                    for attr in ("p", "price_raw"):
                        if hasattr(t, attr):
                            price = getattr(t, attr)
                            break
                if price is None:
                    return Decimal(str(t))
                return Decimal(str(price))
            except Exception:
                continue
    if hasattr(api, "get_bars"):
        try:
            bars = api.get_bars(symbol, "1Min", limit=1)
            try:
                last = bars[symbol][-1]
                return Decimal(str(last.c))
            except Exception:
                try:
                    last = list(bars)[-1]
                    if hasattr(last, "c"):
                        return Decimal(str(last.c))
                    if hasattr(last, "close"):
                        return Decimal(str(last.close))
                    return Decimal(str(last))
                except Exception:
                    pass
        except Exception:
            pass
    raise RuntimeError("Unable to get last trade price for %s with available Alpaca client" % symbol)


def place_order(api, symbol: str, qty, side: str):
    if os.environ.get("DRY_RUN", "true").lower() in ("1", "true", "yes"):
        logger.info("DRY RUN: would %s %s %s", side, qty, symbol)
        return None
    logger.info("Submitting %s order: %s %s", side, symbol, qty)
    order = api.submit_order(symbol=symbol, qty=qty, side=side.lower(), type="market", time_in_force="day")
    logger.info("Order submitted: id=%s status=%s", getattr(order, "id", None), getattr(order, "status", None))
    return order


def can_buy(api, price: Decimal, qty: int) -> bool:
    account = api.get_account()
    buying_power = Decimal(account.buying_power)
    needed = price * qty
    return buying_power >= needed


def owns_at_least(api, symbol: str, qty: int) -> bool:
    try:
        pos = api.get_position(symbol)
        return int(Decimal(pos.qty)) >= qty
    except Exception:
        return False
