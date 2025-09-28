#!/usr/bin/env python3
"""
RSI->GPT->Alpaca trading bot.

Uses TAAPI for RSI data, OpenAI for trading decisions, and Alpaca for order execution.
Configure via environment variables or .env file.
"""
import os
import time
import logging
import threading
from datetime import datetime, time as dtime, timedelta
from decimal import Decimal

import pytz
from dotenv import load_dotenv

from modules.taapi import fetch_rsi_taapi
from modules.gpt_client import ask_gpt_for_decision
from modules.alpaca_client import (
    connect_alpaca,
    get_wallet_amount,
    get_owned_positions,
    get_last_trade_price,
    place_order,
    can_buy,
    owns_at_least,
)
from modules.market_schedule import in_market_hours

load_dotenv()

# Configuration
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

EAST = pytz.timezone("US/Eastern")

# Environment variables
TAAPI_KEY = os.environ.get("TAAPI_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ALPACA_API_KEY = os.environ.get("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.environ.get("ALPACA_SECRET_KEY")
ALPACA_BASE_URL = os.environ.get("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

# Trading configuration
SYMBOL = os.environ.get("SYMBOL", "AAPL")
SYMBOLS_ENV = os.environ.get("SYMBOLS")
if SYMBOLS_ENV:
    SYMBOLS = [s.strip().upper() for s in SYMBOLS_ENV.split(",") if s.strip()]
else:
    SYMBOLS = [SYMBOL]

QTY = int(os.environ.get("QTY", "1"))
DRY_RUN = os.environ.get("DRY_RUN", "true").lower() in ("1", "true", "yes")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")

def setup_file_logging():
    """Setup optional file logging with hourly rotation."""
    LOG_TO_FILE = os.environ.get("LOG_TO_FILE", "false").lower() in ("1", "true", "yes")
    if not LOG_TO_FILE:
        return
    
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logs_dir = os.path.join(base_dir, "log")
        os.makedirs(logs_dir, exist_ok=True)

        tz = pytz.timezone("US/Eastern")

        def make_handler():
            ts = datetime.now(tz).strftime("%m%d%y.%H")
            log_filename = os.path.join(logs_dir, f"TradeBot.{ts}.log")
            fh = logging.FileHandler(log_filename)
            fh.setLevel(LOG_LEVEL)
            fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
            return fh

        # Current file handler stored in a mutable container for rotation
        file_handler = [make_handler()]
        logger.addHandler(file_handler[0])
        logger.info("File logging enabled: %s", file_handler[0].baseFilename)

        def rotator():
            while True:
                try:
                    # Compute seconds until next top of hour in Eastern time
                    now_e = datetime.now(tz)
                    next_hour = (now_e + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
                    sleep_secs = (next_hour - now_e).total_seconds()
                    # Sleep until just after the hour boundary
                    time.sleep(max(1, sleep_secs + 1))

                    new_h = make_handler()
                    logger.addHandler(new_h)
                    # Remove and close old handler
                    old = file_handler[0]
                    logger.removeHandler(old)
                    try:
                        old.close()
                    except Exception:
                        pass
                    file_handler[0] = new_h
                    logger.info("Rotated log file, new file: %s", file_handler[0].baseFilename)
                except Exception:
                    logger.exception("Log rotation failed")
                    # On failure, wait a minute before retrying
                    time.sleep(60)

        t = threading.Thread(target=rotator, daemon=True)
        t.start()
    except Exception:
        logger.exception("Failed to enable file logging")


# Setup file logging
setup_file_logging()


def fetch_rsi(symbol: str) -> Decimal:
    """Fetch RSI value for a symbol using TAAPI."""
    val = fetch_rsi_taapi(symbol, TAAPI_KEY)
    if val is None:
        raise RuntimeError("TAAPI not available or failed to return RSI")
    return val


def _execute_buy_order(api, symbol: str, amount: Decimal, price: Decimal):
    """Execute a buy order with proper logging and validation."""
    try:
        # Log wallet amounts before attempting to buy
        try:
            cash_before = get_wallet_amount(api, "cash")
        except Exception:
            cash_before = None
        try:
            bp_before = get_wallet_amount(api, "buying_power")
        except Exception:
            bp_before = None
        
        logger.info("Wallet before BUY for %s: cash=%s buying_power=%s", 
                   symbol, 
                   str(cash_before) if cash_before is not None else "<unknown>", 
                   str(bp_before) if bp_before is not None else "<unknown>")

        # Determine qty to buy: prefer GPT-provided amount, else use configured QTY
        qty_to_buy = QTY if amount is None else amount

        # Ensure qty_to_buy is numeric
        try:
            qty_numeric = Decimal(qty_to_buy)
        except Exception:
            try:
                qty_numeric = Decimal(str(QTY))
            except Exception:
                qty_numeric = Decimal(0)

        # Check buying power using the last trade price if available
        if price is not None and qty_numeric > 0:
            if not can_buy(api, price, int(qty_numeric) if qty_numeric == qty_numeric.to_integral_value() else float(qty_numeric)):
                logger.info("Insufficient buying power to buy %s %s at %s", qty_numeric, symbol, price)
                return

        # Convert qty_numeric to int when whole number else float (for fractional)
        if qty_numeric == qty_numeric.to_integral_value():
            qty_for_order = int(qty_numeric)
        else:
            qty_for_order = float(qty_numeric)

        place_order(api, symbol, qty_for_order, "buy")
    except Exception as e:
        logger.exception("Error handling BUY for %s: %s", symbol, e)


def _execute_sell_order(api, symbol: str, amount: Decimal):
    """Execute a sell order with proper logging and validation."""
    try:
        # Determine qty to sell: prefer GPT-provided amount, else sell entire position
        try:
            pos = api.get_position(symbol)
        except Exception:
            logger.info("Do not own any %s to sell", symbol)
            return

        try:
            qty_owned = Decimal(str(pos.qty))
        except Exception:
            try:
                qty_owned = Decimal(str(getattr(pos, "qty", 0)))
            except Exception:
                logger.info("Could not determine position quantity for %s", symbol)
                return

        if qty_owned <= 0:
            logger.info("Do not own any %s to sell", symbol)
            return

        if amount is None:
            qty_to_sell = qty_owned
        else:
            try:
                qty_to_sell = Decimal(amount)
            except Exception:
                qty_to_sell = qty_owned

        # Cap qty_to_sell at qty_owned
        if qty_to_sell > qty_owned:
            qty_to_sell = qty_owned

        # Prepare qty for order: integer when whole number, else float for fractional
        if qty_to_sell == qty_to_sell.to_integral_value():
            qty_for_order = int(qty_to_sell)
        else:
            qty_for_order = float(qty_to_sell)

        place_order(api, symbol, qty_for_order, "sell")
        
        # Log wallet amounts after SELL
        try:
            cash_after = get_wallet_amount(api, "cash")
        except Exception:
            cash_after = None
        try:
            pv_after = get_wallet_amount(api, "portfolio_value")
        except Exception:
            pv_after = None
        
        logger.info("Wallet after SELL for %s: cash=%s portfolio_value=%s", 
                   symbol, 
                   str(cash_after) if cash_after is not None else "<unknown>", 
                   str(pv_after) if pv_after is not None else "<unknown>")
    except Exception as e:
        logger.exception("Error handling SELL for %s: %s", symbol, e)


def run_once(api, symbol: str):
    """Execute one trading cycle for a symbol."""
    # Fetch RSI
    try:
        rsi = fetch_rsi(symbol)
        logger.info("RSI for %s = %s", symbol, rsi)
    except Exception as e:
        logger.exception("Failed to fetch RSI for %s: %s", symbol, e)
        return

    # Gather trading context
    try:
        price = get_last_trade_price(api, symbol)
    except Exception:
        price = None

    try:
        owned_positions = get_owned_positions(api)
        shares_owned = owned_positions.get(symbol.upper(), Decimal(0))
    except Exception:
        shares_owned = Decimal(0)

    try:
        wallet_amount = get_wallet_amount(api, "cash")
    except Exception:
        try:
            wallet_amount = get_wallet_amount(api, "buying_power")
        except Exception:
            wallet_amount = Decimal(0)

    # Get GPT trading decision
    try:
        decision, amount = ask_gpt_for_decision(
            OPENAI_API_KEY, OPENAI_MODEL, rsi, symbol, shares_owned, 
            price if price is not None else Decimal(0), wallet_amount
        )
    except Exception as e:
        logger.exception("GPT error when called with extended context for %s: %s", symbol, e)
        return

    # Execute trading decision
    if decision == "BUY":
        _execute_buy_order(api, symbol, amount, price)
    elif decision == "SELL":
        _execute_sell_order(api, symbol, amount)
    else:
        logger.info("Decision NOTHING for %s — no action taken", symbol)


def parse_et_time(s: str):
    """Parse HH:MM time string to time object."""
    try:
        hh, mm = s.split(":")
        return dtime(hour=int(hh), minute=int(mm))
    except Exception:
        return None


def main():
    """Main trading bot loop."""
    logger.info("Starting RSI->GPT->Alpaca bot for %s (DRY_RUN=%s)", SYMBOL, DRY_RUN)
    api = connect_alpaca()

    # Schedule window from environment (HH:MM in ET). If not provided, use market hours.
    sched_start = os.environ.get("SCHEDULE_START")
    sched_end = os.environ.get("SCHEDULE_END")

    start_time = parse_et_time(sched_start) if sched_start else dtime(hour=9, minute=30)
    end_time = parse_et_time(sched_end) if sched_end else dtime(hour=16, minute=0)

    while True:
        now = datetime.now(EAST)

        # If outside the configured schedule window, sleep until the next scheduled start
        today_start = EAST.localize(datetime.combine(now.date(), start_time))
        today_end = EAST.localize(datetime.combine(now.date(), end_time))

        if now < today_start:
            secs = (today_start - now).total_seconds()
            logger.info("Before scheduled start (%s). Sleeping %s seconds until start.", today_start.isoformat(), int(secs))
            time.sleep(max(30, int(secs)))
            continue

        if now > today_end:
            # Sleep until next day's scheduled start
            next_day = now.date() + timedelta(days=1)
            next_start = EAST.localize(datetime.combine(next_day, start_time))
            secs = (next_start - now).total_seconds()
            logger.info("After scheduled end (%s). Sleeping until next start %s seconds.", today_end.isoformat(), int(secs))
            time.sleep(max(60, int(secs)))
            continue

        # If market is closed, wait until market open too
        if not in_market_hours(now):
            logger.info("Market closed at %s. Sleeping until market open.", now.isoformat())
            # Sleep a minute and re-evaluate
            time.sleep(60)
            continue

        # Iterate over configured symbols for this minute
        for sym in SYMBOLS:
            run_once(api, sym)

        # Sleep until the next full minute
        now_local = datetime.now()
        sleep_seconds = 60 - now_local.second
        time.sleep(sleep_seconds)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
