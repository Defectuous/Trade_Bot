"""TAAPI helper: fetch technical indicators via the taapi.io API.

This module provides wrappers around TAAPI that return technical indicators as Decimals.
Supports RSI, MA, EMA, Three Black Crows pattern, ADX, ADXR, Candlestick data, Volume, Bollinger Bands, and DMI indicators.
"""
from decimal import Decimal
import requests
from typing import Optional, Dict, Any
import os


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
        return None
    return None


def fetch_ma_taapi(symbol: str, taapi_key: str, period: int = 20, interval: str = "1m", timeout: int = 10) -> Optional[Decimal]:
    """Fetch Simple Moving Average for `symbol` from taapi.io."""
    if not taapi_key:
        return None
    url = "https://api.taapi.io/ma"
    params = {"secret": taapi_key, "symbol": symbol, "interval": interval, "type": "stocks", "period": period}
    try:
        resp = requests.get(url, params=params, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        if "value" in data:
            return Decimal(str(data["value"]))
    except Exception:
        return None
    return None


def fetch_ema_taapi(symbol: str, taapi_key: str, period: int = 12, interval: str = "1m", timeout: int = 10) -> Optional[Decimal]:
    """Fetch Exponential Moving Average for `symbol` from taapi.io."""
    if not taapi_key:
        return None
    url = "https://api.taapi.io/ema"
    params = {"secret": taapi_key, "symbol": symbol, "interval": interval, "type": "stocks", "period": period}
    try:
        resp = requests.get(url, params=params, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        if "value" in data:
            return Decimal(str(data["value"]))
    except Exception:
        return None
    return None


def fetch_pattern_taapi(symbol: str, taapi_key: str, interval: str = "1m", timeout: int = 10) -> Optional[str]:
    """Fetch Three Black Crows pattern for `symbol` from taapi.io."""
    if not taapi_key:
        return None
    url = "https://api.taapi.io/cdl3blackcrows"
    params = {"secret": taapi_key, "symbol": symbol, "interval": interval, "type": "stocks"}
    try:
        resp = requests.get(url, params=params, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        if "value" in data:
            # Convert pattern value to readable string
            value = data["value"]
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
    except Exception:
        return None
    return None


def fetch_adx_taapi(symbol: str, taapi_key: str, period: int = 14, interval: str = "1m", timeout: int = 10) -> Optional[Decimal]:
    """Fetch ADX (Average Directional Index) for `symbol` from taapi.io."""
    if not taapi_key:
        return None
    url = "https://api.taapi.io/adx"
    params = {"secret": taapi_key, "symbol": symbol, "interval": interval, "type": "stocks", "period": period}
    try:
        resp = requests.get(url, params=params, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        if "value" in data:
            return Decimal(str(data["value"]))
    except Exception:
        return None
    return None


def fetch_adxr_taapi(symbol: str, taapi_key: str, period: int = 14, interval: str = "1m", timeout: int = 10) -> Optional[Decimal]:
    """Fetch ADXR (Average Directional Index Rating) for `symbol` from taapi.io."""
    if not taapi_key:
        return None
    url = "https://api.taapi.io/adxr"
    params = {"secret": taapi_key, "symbol": symbol, "interval": interval, "type": "stocks", "period": period}
    try:
        resp = requests.get(url, params=params, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        if "value" in data:
            return Decimal(str(data["value"]))
    except Exception:
        return None
    return None


def fetch_candle_taapi(symbol: str, taapi_key: str, interval: str = "1m", timeout: int = 10) -> Optional[Dict[str, Decimal]]:
    """Fetch candlestick data (OHLC) for `symbol` from taapi.io.
    
    Returns a dictionary with Open, High, Low, Close prices as Decimals.
    Example return: {'open': Decimal('450.25'), 'high': Decimal('451.80'), 'low': Decimal('449.90'), 'close': Decimal('451.15')}
    """
    if not taapi_key:
        return None
    url = "https://api.taapi.io/candle"
    params = {"secret": taapi_key, "symbol": symbol, "interval": interval, "type": "stocks"}
    try:
        resp = requests.get(url, params=params, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        
        # TAAPI candle endpoint returns OHLC data
        if all(key in data for key in ['open', 'high', 'low', 'close']):
            return {
                'open': Decimal(str(data['open'])),
                'high': Decimal(str(data['high'])), 
                'low': Decimal(str(data['low'])),
                'close': Decimal(str(data['close']))
            }
    except Exception:
        return None
    return None


def fetch_volume_taapi(symbol: str, taapi_key: str, interval: str = "1m", timeout: int = 10) -> Optional[Decimal]:
    """Fetch Volume for `symbol` from taapi.io.
    
    Returns the trading volume as a Decimal on success, or None if taapi_key is missing or an error occurs.
    """
    if not taapi_key:
        return None
    url = "https://api.taapi.io/volume"
    params = {"secret": taapi_key, "symbol": symbol, "interval": interval, "type": "stocks"}
    try:
        resp = requests.get(url, params=params, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        if "value" in data:
            return Decimal(str(data["value"]))
    except Exception:
        return None
    return None


def fetch_bbands_taapi(symbol: str, taapi_key: str, period: int = 20, interval: str = "1m", timeout: int = 10) -> Optional[Dict[str, Decimal]]:
    """Fetch Bollinger Bands for `symbol` from taapi.io.
    
    Returns a dictionary with upper, middle, and lower bands as Decimals.
    Example return: {'upper': Decimal('452.50'), 'middle': Decimal('450.00'), 'lower': Decimal('447.50')}
    """
    if not taapi_key:
        return None
    url = "https://api.taapi.io/bbands"
    params = {"secret": taapi_key, "symbol": symbol, "interval": interval, "type": "stocks", "period": period}
    try:
        resp = requests.get(url, params=params, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        
        # TAAPI bbands endpoint returns upper, middle, lower bands
        if all(key in data for key in ['valueUpperBand', 'valueMiddleBand', 'valueLowerBand']):
            return {
                'upper': Decimal(str(data['valueUpperBand'])),
                'middle': Decimal(str(data['valueMiddleBand'])), 
                'lower': Decimal(str(data['valueLowerBand']))
            }
    except Exception:
        return None
    return None


def fetch_dmi_taapi(symbol: str, taapi_key: str, period: int = 14, interval: str = "1m", timeout: int = 10) -> Optional[Dict[str, Decimal]]:
    """Fetch DMI (Directional Movement Index) for `symbol` from taapi.io.
    
    Returns a dictionary with DI+, DI-, and DX values as Decimals.
    Example return: {'di_plus': Decimal('25.30'), 'di_minus': Decimal('18.75'), 'dx': Decimal('14.80')}
    """
    if not taapi_key:
        return None
    url = "https://api.taapi.io/dmi"
    params = {"secret": taapi_key, "symbol": symbol, "interval": interval, "type": "stocks", "period": period}
    try:
        resp = requests.get(url, params=params, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        
        # TAAPI dmi endpoint returns DI+, DI-, and DX
        if all(key in data for key in ['valueDIPlus', 'valueDIMinus', 'valueDX']):
            return {
                'di_plus': Decimal(str(data['valueDIPlus'])),
                'di_minus': Decimal(str(data['valueDIMinus'])), 
                'dx': Decimal(str(data['valueDX']))
            }
    except Exception:
        return None
    return None


def fetch_all_indicators(symbol: str, taapi_key: str, interval: str = "1m") -> Dict[str, Any]:
    """Fetch all technical indicators for a symbol.
    
    Returns a dictionary containing all indicator values or None for failed fetches.
    Individual indicator failures are logged but don't prevent other indicators from being fetched.
    Indicators can be enabled/disabled via environment variables (ENABLE_RSI, ENABLE_MA, etc.).
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Get periods from environment variables with defaults
    ma_period = int(os.getenv('MA_PERIOD', 20))
    ema_period = int(os.getenv('EMA_PERIOD', 12))
    adx_period = int(os.getenv('ADX_PERIOD', 14))
    adxr_period = int(os.getenv('ADXR_PERIOD', 14))
    bbands_period = int(os.getenv('BBANDS_PERIOD', 20))
    dmi_period = int(os.getenv('DMI_PERIOD', 14))
    
    # Get indicator enable/disable flags from environment variables
    def is_indicator_enabled(indicator_name: str) -> bool:
        """Check if an indicator is enabled via environment variable."""
        env_var = f"ENABLE_{indicator_name.upper()}"
        return os.getenv(env_var, 'true').lower() in ('true', '1', 'yes', 'on')
    
    indicators = {}
    failed_indicators = []
    disabled_indicators = []
    
    # Fetch each indicator individually with error handling and enable/disable checks
    if is_indicator_enabled('rsi'):
        try:
            indicators['rsi'] = fetch_rsi_taapi(symbol, taapi_key, interval)
            if indicators['rsi'] is None:
                failed_indicators.append('RSI')
        except Exception as e:
            logger.debug("RSI fetch failed for %s: %s", symbol, e)
            indicators['rsi'] = None
            failed_indicators.append('RSI')
    else:
        indicators['rsi'] = None
        disabled_indicators.append('RSI')
    
    if is_indicator_enabled('ma'):
        try:
            indicators['ma'] = fetch_ma_taapi(symbol, taapi_key, ma_period, interval)
            if indicators['ma'] is None:
                failed_indicators.append('MA')
        except Exception as e:
            logger.debug("MA fetch failed for %s: %s", symbol, e)
            indicators['ma'] = None
            failed_indicators.append('MA')
    else:
        indicators['ma'] = None
        disabled_indicators.append('MA')
    
    if is_indicator_enabled('ema'):
        try:
            indicators['ema'] = fetch_ema_taapi(symbol, taapi_key, ema_period, interval)
            if indicators['ema'] is None:
                failed_indicators.append('EMA')
        except Exception as e:
            logger.debug("EMA fetch failed for %s: %s", symbol, e)
            indicators['ema'] = None
            failed_indicators.append('EMA')
    else:
        indicators['ema'] = None
        disabled_indicators.append('EMA')
    
    if is_indicator_enabled('pattern'):
        try:
            indicators['pattern'] = fetch_pattern_taapi(symbol, taapi_key, interval)
            if indicators['pattern'] is None:
                failed_indicators.append('Pattern')
        except Exception as e:
            logger.debug("Pattern fetch failed for %s: %s", symbol, e)
            indicators['pattern'] = None
            failed_indicators.append('Pattern')
    else:
        indicators['pattern'] = None
        disabled_indicators.append('Pattern')
    
    if is_indicator_enabled('adx'):
        try:
            indicators['adx'] = fetch_adx_taapi(symbol, taapi_key, adx_period, interval)
            if indicators['adx'] is None:
                failed_indicators.append('ADX')
        except Exception as e:
            logger.debug("ADX fetch failed for %s: %s", symbol, e)
            indicators['adx'] = None
            failed_indicators.append('ADX')
    else:
        indicators['adx'] = None
        disabled_indicators.append('ADX')
    
    if is_indicator_enabled('adxr'):
        try:
            indicators['adxr'] = fetch_adxr_taapi(symbol, taapi_key, adxr_period, interval)
            if indicators['adxr'] is None:
                failed_indicators.append('ADXR')
        except Exception as e:
            logger.debug("ADXR fetch failed for %s: %s", symbol, e)
            indicators['adxr'] = None
            failed_indicators.append('ADXR')
    else:
        indicators['adxr'] = None
        disabled_indicators.append('ADXR')
    
    if is_indicator_enabled('candle'):
        try:
            indicators['candle'] = fetch_candle_taapi(symbol, taapi_key, interval)
            if indicators['candle'] is None:
                failed_indicators.append('Candle')
        except Exception as e:
            logger.debug("Candle fetch failed for %s: %s", symbol, e)
            indicators['candle'] = None
            failed_indicators.append('Candle')
    else:
        indicators['candle'] = None
        disabled_indicators.append('Candle')
    
    if is_indicator_enabled('volume'):
        try:
            indicators['volume'] = fetch_volume_taapi(symbol, taapi_key, interval)
            if indicators['volume'] is None:
                failed_indicators.append('Volume')
        except Exception as e:
            logger.debug("Volume fetch failed for %s: %s", symbol, e)
            indicators['volume'] = None
            failed_indicators.append('Volume')
    else:
        indicators['volume'] = None
        disabled_indicators.append('Volume')
    
    if is_indicator_enabled('bbands'):
        try:
            indicators['bbands'] = fetch_bbands_taapi(symbol, taapi_key, bbands_period, interval)
            if indicators['bbands'] is None:
                failed_indicators.append('BBands')
        except Exception as e:
            logger.debug("BBands fetch failed for %s: %s", symbol, e)
            indicators['bbands'] = None
            failed_indicators.append('BBands')
    else:
        indicators['bbands'] = None
        disabled_indicators.append('BBands')
    
    if is_indicator_enabled('dmi'):
        try:
            indicators['dmi'] = fetch_dmi_taapi(symbol, taapi_key, dmi_period, interval)
            if indicators['dmi'] is None:
                failed_indicators.append('DMI')
        except Exception as e:
            logger.debug("DMI fetch failed for %s: %s", symbol, e)
            indicators['dmi'] = None
            failed_indicators.append('DMI')
    else:
        indicators['dmi'] = None
        disabled_indicators.append('DMI')
    
    # Log summary of successful, failed, and disabled indicators
    successful_indicators = [name.upper() for name, value in indicators.items() if value is not None]
    
    if successful_indicators:
        logger.info("Successfully fetched indicators for %s: %s", symbol, ', '.join(successful_indicators))
    
    if failed_indicators:
        logger.warning("Failed to fetch indicators for %s: %s", symbol, ', '.join(failed_indicators))
    
    if disabled_indicators:
        logger.info("Disabled indicators for %s: %s", symbol, ', '.join(disabled_indicators))
    
    return indicators
