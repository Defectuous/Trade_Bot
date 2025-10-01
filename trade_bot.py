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
import requests
from dotenv import load_dotenv

from modules.taapi import fetch_rsi_taapi, fetch_all_indicators
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
from modules.discord_webhook import (
    send_trading_day_summary,
    send_trade_notification,
    get_discord_webhook_url,
)

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
DISCORD_WEBHOOK_URL = get_discord_webhook_url()

# Trading configuration
SYMBOL = os.environ.get("SYMBOL", "AAPL")
SYMBOLS_ENV = os.environ.get("SYMBOLS")
if SYMBOLS_ENV:
    SYMBOLS = [s.strip().upper() for s in SYMBOLS_ENV.split(",") if s.strip()]
else:
    SYMBOLS = [SYMBOL]

QTY_ENV = os.environ.get("QTY", "1")
try:
    # Support both integer and fractional QTY values
    QTY = Decimal(QTY_ENV)
    logger.info("Configured default QTY: %s shares", QTY)
except Exception:
    QTY = Decimal("1")
    logger.warning("Invalid QTY value '%s', using default QTY=1", QTY_ENV)
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


def fetch_all_technical_indicators(symbol: str) -> dict:
    """Fetch all technical indicators for enhanced trading analysis."""
    indicators = fetch_all_indicators(symbol, TAAPI_KEY)
    if not indicators:
        raise RuntimeError("Failed to fetch technical indicators from TAAPI")
    
    # Count valid indicators
    valid_count = sum(1 for v in indicators.values() if v is not None and v != 'N/A')
    total_count = len(indicators)
    
    logger.info("Technical indicators for %s: %d/%d valid indicators retrieved", 
               symbol, valid_count, total_count)
    
    # Only log details if at least one indicator is valid
    if valid_count > 0:
        valid_indicators = []
        for name, value in indicators.items():
            if value is not None and value != 'N/A':
                valid_indicators.append(f"{name.upper()}={value}")
        logger.debug("Valid indicators for %s: %s", symbol, ', '.join(valid_indicators))
    
    return indicators


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
        
        # Log the decision source for transparency
        if amount is not None:
            logger.info("Using GPT-recommended quantity: %s shares for %s", amount, symbol)
        else:
            logger.info("Using configured default quantity: %s shares for %s", QTY, symbol)

        # Ensure qty_to_buy is numeric
        try:
            qty_numeric = Decimal(qty_to_buy)
        except Exception:
            try:
                qty_numeric = Decimal(str(QTY))
            except Exception:
                qty_numeric = Decimal(0)

        # Safety check: Cap order to available cash (prevent GPT over-recommendations)
        if price is not None and qty_numeric > 0:
            try:
                current_cash = get_wallet_amount(api, "cash")
                
                # Add safety margin (keep some cash for fees/margin)
                safety_margin = Decimal("0.02")  # 2% safety margin
                usable_cash = current_cash * (Decimal("1") - safety_margin)
                
                max_affordable_shares = usable_cash / price
                
                if qty_numeric > max_affordable_shares:
                    logger.warning("GPT recommended %s shares ($%s), but only $%s available (after %s%% safety margin). Capping to %s shares ($%s)", 
                                 qty_numeric, qty_numeric * price, usable_cash, 
                                 safety_margin * 100, max_affordable_shares, max_affordable_shares * price)
                    qty_numeric = max_affordable_shares
                    
                    # Update the decision source logging
                    logger.info("Using cash-limited quantity: %s shares for %s (GPT recommended %s)", 
                               qty_numeric, symbol, qty_to_buy)
                
                # Additional check: Ensure we have minimum viable quantity
                if qty_numeric <= 0:
                    logger.warning("Insufficient funds to buy any shares of %s at $%s (available: $%s)", 
                                 symbol, price, current_cash)
                    return
                    
            except Exception as e:
                logger.warning("Could not verify cash limits: %s", e)
                # If we can't check cash, fall back to buying power check only

        # Check buying power using the last trade price if available
        if price is not None and qty_numeric > 0:
            # Minimum order value check (prevent tiny orders)
            order_value = price * qty_numeric
            min_order_value = Decimal("1.00")  # $1 minimum order
            
            if order_value < min_order_value:
                logger.warning("Order value $%s below minimum $%s for %s shares of %s", 
                             order_value, min_order_value, qty_numeric, symbol)
                return
            
            # Pass qty_numeric directly - can_buy now supports both int and float
            if not can_buy(api, price, qty_numeric):
                logger.info("Insufficient buying power to buy %s %s at %s", qty_numeric, symbol, price)
                return

        # Convert qty_numeric to int when whole number else float (for fractional)
        if qty_numeric == qty_numeric.to_integral_value():
            qty_for_order = int(qty_numeric)
        else:
            qty_for_order = float(qty_numeric)

        place_order(api, symbol, qty_for_order, "buy")
        logger.info("✅ BUY order submitted successfully for %s %s", qty_for_order, symbol)
        
        # Send Discord notification for buy order
        if DISCORD_WEBHOOK_URL:
            send_trade_notification(
                DISCORD_WEBHOOK_URL, "BUY", symbol, 
                Decimal(str(qty_for_order)), price
            )
    except Exception as e:
        error_msg = str(e)
        logger.exception("Error handling BUY for %s: %s", symbol, e)
        
        # Check if it's a server error that might be temporary
        if any(keyword in error_msg for keyword in ['500', '502', '503', '504', 'Server Error', 'Internal Server Error']):
            logger.warning("🚨 Alpaca server error detected for BUY order on %s. This is likely temporary - will retry on next trading cycle.", symbol)
        
        # Send Discord notification about failed order if webhook is configured
        if DISCORD_WEBHOOK_URL:
            try:
                from modules.discord_webhook import send_error_notification
                send_error_notification(DISCORD_WEBHOOK_URL, f"❌ BUY order failed for {symbol}", error_msg)
            except Exception:
                pass  # Don't let Discord notification failures break the trading loop


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
        logger.info("✅ SELL order submitted successfully for %s %s", qty_for_order, symbol)
        
        # Send Discord notification for sell order
        if DISCORD_WEBHOOK_URL:
            # Get current price for notification
            try:
                current_price = get_last_trade_price(api, symbol)
            except Exception:
                current_price = None
            
            send_trade_notification(
                DISCORD_WEBHOOK_URL, "SELL", symbol,
                qty_to_sell, current_price
            )
        
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
        error_msg = str(e)
        logger.exception("Error handling SELL for %s: %s", symbol, e)
        
        # Check if it's a server error that might be temporary
        if any(keyword in error_msg for keyword in ['500', '502', '503', '504', 'Server Error', 'Internal Server Error']):
            logger.warning("🚨 Alpaca server error detected for SELL order on %s. This is likely temporary - will retry on next trading cycle.", symbol)
        
        # Send Discord notification about failed order if webhook is configured
        if DISCORD_WEBHOOK_URL:
            try:
                from modules.discord_webhook import send_error_notification
                send_error_notification(DISCORD_WEBHOOK_URL, f"❌ SELL order failed for {symbol}", error_msg)
            except Exception:
                pass  # Don't let Discord notification failures break the trading loop


def run_once(api, symbol: str):
    """Execute one trading cycle for a symbol using enhanced technical analysis."""
    # Fetch all technical indicators
    try:
        indicators = fetch_all_technical_indicators(symbol)
        logger.info("Enhanced indicators for %s fetched successfully", symbol)
    except Exception as e:
        logger.exception("Failed to fetch enhanced indicators for %s: %s", symbol, e)
        # Fallback to RSI-only mode
        try:
            rsi = fetch_rsi(symbol)
            indicators = {'rsi': rsi, 'ma': 'N/A', 'ema': 'N/A', 'pattern': 'N/A', 'adx': 'N/A', 'adxr': 'N/A'}
            logger.info("Fallback RSI for %s = %s", symbol, rsi)
        except Exception as e2:
            logger.exception("Failed to fetch fallback RSI for %s: %s", symbol, e2)
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
        logger.info("Retrieved cash balance for GPT: $%s", wallet_amount)
    except Exception:
        try:
            wallet_amount = get_wallet_amount(api, "buying_power")
            logger.info("Retrieved buying power for GPT (cash unavailable): $%s", wallet_amount)
        except Exception:
            wallet_amount = Decimal(0)
            logger.warning("Could not retrieve wallet amount, using $0 for GPT prompt")

    # Get GPT trading decision using enhanced indicators
    try:
        decision, amount = ask_gpt_for_decision(
            OPENAI_API_KEY, OPENAI_MODEL, indicators, symbol, shares_owned, 
            price if price is not None else Decimal(0), wallet_amount
        )
    except Exception as e:
        logger.exception("GPT error when called with enhanced indicators for %s: %s", symbol, e)
        return

    # Execute trading decision
    if decision == "BUY":
        _execute_buy_order(api, symbol, amount, price)
    elif decision == "SELL":
        _execute_sell_order(api, symbol, amount)
    else:
        logger.info("Decision NOTHING for %s — no action taken", symbol)


def send_daily_summary(api, day_type: str = "start"):
    """Send daily trading summary to Discord.
    
    Args:
        api: Alpaca API client
        day_type: "start" or "end" of trading day
    """
    if not DISCORD_WEBHOOK_URL:
        return
    
    try:
        # Get wallet total
        try:
            wallet_total = get_wallet_amount(api, "portfolio_value")
        except Exception:
            try:
                wallet_total = get_wallet_amount(api, "cash")
            except Exception:
                wallet_total = Decimal(0)
        
        # Get current positions
        try:
            positions = get_owned_positions(api)
        except Exception:
            positions = {}
        
        # Send Discord summary
        send_trading_day_summary(
            DISCORD_WEBHOOK_URL, wallet_total, positions, day_type
        )
        
    except Exception as e:
        logger.exception("Failed to send Discord daily summary: %s", e)


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

    # Track if we've sent daily summaries
    sent_start_summary = False
    sent_end_summary = False
    last_trading_date = None

    while True:
        now = datetime.now(EAST)
        current_date = now.date()

        # Reset daily summary flags for new trading day
        if last_trading_date != current_date:
            sent_start_summary = False
            sent_end_summary = False
            last_trading_date = current_date

        # If outside the configured schedule window, sleep until the next scheduled start
        today_start = EAST.localize(datetime.combine(now.date(), start_time))
        today_end = EAST.localize(datetime.combine(now.date(), end_time))

        if now < today_start:
            secs = (today_start - now).total_seconds()
            logger.info("Before scheduled start (%s). Sleeping %s seconds until start.", today_start.isoformat(), int(secs))
            time.sleep(max(30, int(secs)))
            continue

        if now > today_end:
            # Send end-of-day summary if we haven't already
            if not sent_end_summary and in_market_hours():
                send_daily_summary(api, "end")
                sent_end_summary = True
            
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

        # Send start-of-day summary if we haven't already and market just opened
        if not sent_start_summary:
            send_daily_summary(api, "start")
            sent_start_summary = True

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
