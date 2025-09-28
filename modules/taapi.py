"""TAAPI helper: fetch RSI via the taapi.io API.

This module provides a small wrapper around TAAPI that returns a Decimal RSI.
It keeps dependencies minimal (requests) and is safe to import without API keys.
"""
from decimal import Decimal
import requests
from typing import Optional


def fetch_rsi_taapi(symbol: str, taapi_key: str, interval: str = "1m", timeout: int = 10) -> Optional[Decimal]:
    """Fetch RSI for `symbol` from taapi.io.

    Returns a Decimal RSI on success, or None if taapi_key is missing or an error occurs.
    """
    if not taapi_key:
        return None
    url = "https://api.taapi.io/rsi"
    params = {"secret": taapi_key, "symbol": symbol, "interval": interval, "type": "stocks"}
    try:
        resp = requests.get(url, params=params, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        if "value" in data:
            return Decimal(str(data["value"]))
    except Exception:
        # let the caller handle fallback
        return None
    return None
import requests
from decimal import Decimal

from typing import Optional


def fetch_rsi_taapi(symbol: str, taapi_key: str, interval: str = "1m") -> Decimal:
    """
    Fetch RSI from TAAPI.io for the given symbol and return as Decimal.
    This is a thin wrapper around the existing TAAPI HTTP API.
    """
    if not taapi_key:
        raise RuntimeError("TAAPI key not provided")
    url = "https://api.taapi.io/rsi"
    params = {"secret": taapi_key, "symbol": symbol, "interval": interval, "type": "stocks"}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if "value" not in data:
        raise RuntimeError(f"Unexpected TAAPI response: {data}")
    return Decimal(str(data["value"]))
