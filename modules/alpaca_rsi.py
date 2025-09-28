from decimal import Decimal, getcontext
from typing import List, Sequence
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Increase decimal precision for financial calculations
getcontext().prec = 12


def _decimal_list(values: Sequence[float]) -> List[Decimal]:
    return [Decimal(str(v)) for v in values]


def compute_rsi_from_closes(closes: Sequence[float], period: int = 14) -> Decimal:
    """
    Compute RSI (Wilder's smoothing) from a sequence of close prices.
    Returns a Decimal RSI value.

    closes: sequence of floats or numbers. Must have at least period+1 elements.
    period: RSI period (default 14)
    """
    if len(closes) < period + 1:
        raise ValueError(f"Need at least {period+1} closes to compute RSI, got {len(closes)}")

    closes_d = _decimal_list(closes)

    gains = []
    losses = []

    for i in range(1, len(closes_d)):
        diff = closes_d[i] - closes_d[i - 1]
        if diff > 0:
            gains.append(diff)
            losses.append(Decimal('0'))
        else:
            gains.append(Decimal('0'))
            losses.append(-diff)

    # Seed average gain/loss using simple average over first `period` entries
    seed_gains = gains[:period]
    seed_losses = losses[:period]

    avg_gain = sum(seed_gains, Decimal('0')) / Decimal(period)
    avg_loss = sum(seed_losses, Decimal('0')) / Decimal(period)

    # Wilder smoothing for subsequent values
    for i in range(period, len(gains)):
        g = gains[i]
        l = losses[i]
        avg_gain = (avg_gain * (Decimal(period - 1)) + g) / Decimal(period)
        avg_loss = (avg_loss * (Decimal(period - 1)) + l) / Decimal(period)

    if avg_loss == 0:
        return Decimal('100')

    rs = avg_gain / avg_loss
    rsi = Decimal('100') - (Decimal('100') / (Decimal('1') + rs))
    return rsi


def fetch_closes_from_alpaca(api, symbol: str, timeframe: str = "1Min", limit: int = 100) -> List[float]:
    """
    Fetch recent close prices from Alpaca client and return a list of floats (chronological order).

    api: Alpaca REST client instance
    symbol: ticker symbol
    timeframe: bar timeframe string accepted by your Alpaca client e.g. '1Min', '5Min', '1D'
    limit: number of bars to fetch
    """
    # Prefer the modern `get_bars` interface if available
    if hasattr(api, "get_bars"):
        try:
            bars = api.get_bars(symbol, timeframe, limit=limit)
        except Exception:
            # get_bars failed (network, auth, etc.) -> let caller handle
            raise

        # Normalize bars to an iterable sequence
        seq = None
        # If bars is a mapping {symbol: [bars]}
        if isinstance(bars, dict):
            seq = bars.get(symbol, None) or list(bars.values())[0] if bars else None
        else:
            try:
                seq = list(bars)
            except Exception:
                seq = bars

        closes = []

        # pandas DataFrame support
        try:
            import pandas as _pd
            if hasattr(seq, 'columns') and isinstance(seq, _pd.DataFrame):
                if 'c' in seq.columns:
                    closes = [float(x) for x in seq['c'].tolist()]
                    logger.debug("Parsed %d closes from pandas DataFrame (c column)", len(closes))
                    return closes
                if 'close' in seq.columns:
                    closes = [float(x) for x in seq['close'].tolist()]
                    logger.debug("Parsed %d closes from pandas DataFrame (close column)", len(closes))
                    return closes
        except Exception:
            # pandas not installed or seq isn't a DataFrame
            pass

        # Iterate and extract close values from each bar-like item
        for b in seq or []:
            try:
                if b is None:
                    continue
                # dict-like
                if isinstance(b, dict):
                    if 'c' in b:
                        closes.append(float(b['c']))
                        continue
                    if 'close' in b:
                        closes.append(float(b['close']))
                        continue
                # object with attributes
                if hasattr(b, 'c'):
                    closes.append(float(getattr(b, 'c')))
                    continue
                if hasattr(b, 'close'):
                    closes.append(float(getattr(b, 'close')))
                    continue
                # sequence/tuple (try common positions: [open, high, low, close] -> index 3 or 4)
                try:
                    if isinstance(b, (list, tuple)) and len(b) >= 4:
                        closes.append(float(b[3]))
                        continue
                except Exception:
                    pass
                # fallback to numeric conversion
                closes.append(float(b))
            except Exception:
                # skip entries we can't parse
                logger.debug("Skipping unparsable bar entry: %r", b)

        if closes:
            logger.debug("Parsed %d closes from get_bars path", len(closes))
            return closes

    # Fallback for older SDKs with get_barset (alpaca-trade-api)
    if hasattr(api, 'get_barset'):
        try:
            barset = api.get_barset(symbol, timeframe, limit=limit)
            bars = barset.get(symbol) if isinstance(barset, dict) else barset
            closes = []
            for b in bars:
                try:
                    if hasattr(b, 'c'):
                        closes.append(float(b.c))
                    elif hasattr(b, 'close'):
                        closes.append(float(b.close))
                    elif isinstance(b, dict) and 'c' in b:
                        closes.append(float(b['c']))
                except Exception:
                    logger.debug("Skipping unparsable bar in get_barset: %r", b)
            if closes:
                logger.debug("Parsed %d closes from get_barset path", len(closes))
                return closes
        except Exception:
            pass

    # As last resort, try latest trades endpoint repeatedly (less ideal)
    closes = []
    try:
        if hasattr(api, 'get_last_trade'):
            # Try a single latest trade first
            t = api.get_last_trade(symbol)
            price = None
            if hasattr(t, 'price'):
                price = getattr(t, 'price')
            elif isinstance(t, dict) and 'price' in t:
                price = t['price']
            if price is not None:
                closes.append(float(price))
    except Exception:
        # ignore
        pass

    if not closes:
        raise RuntimeError('Unable to fetch close prices for %s from Alpaca client' % symbol)

    logger.debug("Returning %d closes for %s", len(closes), symbol)
    return closes


def get_rsi_from_alpaca(api, symbol: str, period: int = 14, timeframe: str = '1Min', limit: int = 100) -> Decimal:
    """
    Fetch closes from Alpaca and compute the RSI using compute_rsi_from_closes.
    Returns a Decimal RSI.
    """
    closes = fetch_closes_from_alpaca(api, symbol, timeframe=timeframe, limit=limit)
    # use the most recent 'period+1' closes for RSI calculation
    if len(closes) < period + 1:
        raise RuntimeError(f'Not enough bars to compute RSI for {symbol}: got {len(closes)}')

    # ensure chronological order and take the most recent period+1
    closes = list(closes)[- (period + 1) :]
    return compute_rsi_from_closes(closes, period=period)


if __name__ == '__main__':
    # Simple CLI to run the RSI computation independently.
    import argparse
    import os

    parser = argparse.ArgumentParser(description='Compute RSI from Alpaca or sample data')
    parser.add_argument('--symbol', '-s', default='AAPL', help='Ticker symbol')
    parser.add_argument('--period', '-p', type=int, default=14, help='RSI period')
    parser.add_argument('--timeframe', '-t', default='1Min', help='Bar timeframe')
    parser.add_argument('--limit', '-l', type=int, default=100, help='Number of bars to fetch')
    parser.add_argument('--use-alpaca', action='store_true', help='Attempt to fetch bars from Alpaca (requires credentials)')
    args = parser.parse_args()

    def _print(msg):
        print(msg)

    if args.use_alpaca:
        try:
            # Try several import strategies so the script works whether run from
            # project root (python modules/alpaca_rsi.py) or from the modules/ folder.
            try:
                # preferred when running from project root
                from modules.alpaca_client import connect_alpaca
            except Exception:
                try:
                    # when cwd is modules/
                    from alpaca_client import connect_alpaca
                except Exception:
                    # as a last resort, add parent directory to sys.path and retry
                    import sys, os as _os
                    parent = _os.path.dirname(_os.path.dirname(__file__))
                    if parent not in sys.path:
                        sys.path.insert(0, parent)
                    from modules.alpaca_client import connect_alpaca

            # Ensure the project's .env (parent of modules/) is loaded so
            # connect_alpaca() can read credentials from it when called without args.
            try:
                from dotenv import load_dotenv
            except Exception:
                load_dotenv = None

            if load_dotenv is not None:
                import os as _os
                project_root = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), '..'))
                dotenv_path = _os.path.join(project_root, '.env')
                if _os.path.exists(dotenv_path):
                    load_dotenv(dotenv_path)
                else:
                    # attempt default load (cwd/.env)
                    load_dotenv()

            api = connect_alpaca()
            _print(f'Connected to Alpaca, fetching bars for {args.symbol}...')
            rsi = get_rsi_from_alpaca(api, args.symbol, period=args.period, timeframe=args.timeframe, limit=args.limit)
            _print(f'RSI({args.period}) for {args.symbol} = {rsi}')
        except Exception as e:
            _print(f'Alpaca fetch failed: {e}')
            _print('Falling back to sample data')
            args.use_alpaca = False

    if not args.use_alpaca:
        # Use a well-known sample closes list (from typical RSI examples)
        sample_closes = [44.34,44.09,44.15,43.61,44.33,44.83,45.10,45.42,45.84,46.08,45.89,46.03,45.61,46.28,46.28]
        try:
            rsi = compute_rsi_from_closes(sample_closes, period=args.period)
            _print(f'Sample RSI({args.period}) = {rsi}')
        except Exception as e:
            _print(f'Failed to compute RSI from sample data: {e}')
            raise
