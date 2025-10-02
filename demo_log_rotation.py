#!/usr/bin/env python3
"""
Demonstration script showing the complete hourly log rotation behavior.
This script simulates the trading bot behavior across an hour boundary.
"""
import os
import time
import logging
import threading
from datetime import datetime, timedelta
import pytz

def demonstrate_hourly_rotation():
    """Demonstrate the complete hourly log rotation cycle."""
    print("🕒 Enhanced Hourly Log Rotation Demonstration")
    print("=" * 55)
    
    # Ensure log directory exists
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(base_dir, "log")
    os.makedirs(logs_dir, exist_ok=True)
    
    tz = pytz.timezone("US/Eastern")
    current_log = os.path.join(logs_dir, "TradeBot.log")
    
    print(f"📁 Log directory: {logs_dir}")
    print(f"🌍 Timezone: US/Eastern")
    
    # Show current time and next rotation time
    now_et = datetime.now(tz)
    next_hour = (now_et + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    time_until_rotation = (next_hour - now_et).total_seconds()
    
    print(f"⏰ Current time: {now_et.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"⏰ Next rotation: {next_hour.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"⏱️  Time until rotation: {int(time_until_rotation)} seconds")
    
    # Set up logging to simulate the bot's behavior
    demo_logger = logging.getLogger("demo_bot")
    demo_logger.setLevel(logging.INFO)
    
    # Remove any existing handlers
    for handler in demo_logger.handlers[:]:
        demo_logger.removeHandler(handler)
    
    # Add console handler for demo output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    demo_logger.addHandler(console_handler)
    
    def create_current_handler():
        """Create handler for current log file (TradeBot.log)."""
        handler = logging.FileHandler(current_log)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        return handler
    
    def rename_current_log():
        """Rename current log file to timestamped format."""
        if os.path.exists(current_log):
            try:
                # Use the previous hour's timestamp
                prev_hour = datetime.now(tz) - timedelta(hours=1)
                ts = prev_hour.strftime("%m%d%y.%H")
                archived_log = os.path.join(logs_dir, f"TradeBot.{ts}.log")
                os.rename(current_log, archived_log)
                demo_logger.info(f"Log rotated: TradeBot.log -> TradeBot.{ts}.log")
                return f"TradeBot.{ts}.log"
            except Exception as e:
                demo_logger.error(f"Failed to rename log file: {e}")
                return None
        return None
    
    # Phase 1: Normal logging operations
    print(f"\n✅ Phase 1: Normal Trading Bot Operations")
    print(f"   📝 Writing to current log: TradeBot.log")
    
    file_handler = create_current_handler()
    demo_logger.addHandler(file_handler)
    
    # Simulate normal bot activity
    demo_logger.info("Trading bot started - Enhanced logging enabled")
    demo_logger.info("Market hours check: Trading session active")
    demo_logger.info("Fetching technical indicators for AAPL...")
    demo_logger.info("RSI: 45.2, MA: 150.45, EMA: 149.80, ADX: 25.4")
    demo_logger.info("GPT decision: BUY 1 share of AAPL at $150.45")
    demo_logger.info("Order placed successfully - Order ID: demo_12345")
    
    # Show current log status
    if os.path.exists(current_log):
        size = os.path.getsize(current_log)
        print(f"   📊 Current log size: {size} bytes")
    
    # Phase 2: Simulate waiting for hour change (we'll simulate this quickly)
    print(f"\n⏳ Phase 2: Simulating hour boundary (normally waits until top of hour)")
    print(f"   🎭 [Simulating time passage...]")
    
    # Wait a moment to simulate some time passing
    time.sleep(1)
    
    # Add more activity before rotation
    demo_logger.info("Continuing trading operations...")
    demo_logger.info("Market check: 15 minutes until market close")
    demo_logger.info("Portfolio update: +$125.50 unrealized P&L")
    
    # Phase 3: Hour rotation
    print(f"\n🔄 Phase 3: Hourly Log Rotation")
    
    # Close current handler
    demo_logger.removeHandler(file_handler)
    file_handler.close()
    
    # Rename current log
    archived_name = rename_current_log()
    if archived_name:
        print(f"   📦 Archived: {archived_name}")
    
    # Create new current log
    new_handler = create_current_handler()
    demo_logger.addHandler(new_handler)
    
    print(f"   📄 New log created: TradeBot.log")
    
    # Phase 4: Continue with new log
    print(f"\n✅ Phase 4: Continuing with Fresh Log")
    
    demo_logger.info("New hour started - Log rotation completed")
    demo_logger.info("Continuing trading operations in fresh log file")
    demo_logger.info("Technical analysis: Market showing bullish momentum")
    demo_logger.info("Position update: Holding 1 share of AAPL")
    
    # Clean up
    demo_logger.removeHandler(new_handler)
    new_handler.close()
    
    # Show final results
    print(f"\n📂 Final Log Directory Contents:")
    try:
        log_files = [f for f in os.listdir(logs_dir) if f.startswith("TradeBot")]
        for log_file in sorted(log_files):
            file_path = os.path.join(logs_dir, log_file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                mtime = os.path.getmtime(file_path)
                mtime_str = datetime.fromtimestamp(mtime).strftime("%H:%M:%S")
                print(f"   📄 {log_file} ({size} bytes, {mtime_str})")
    except Exception as e:
        print(f"   ❌ Error listing files: {e}")
    
    # Show content verification
    print(f"\n🔍 Content Verification:")
    
    # Check archived log
    if archived_name and os.path.exists(os.path.join(logs_dir, archived_name)):
        try:
            with open(os.path.join(logs_dir, archived_name), 'r') as f:
                lines = f.readlines()
                pre_rotation_msgs = [line for line in lines if "Trading bot started" in line or "GPT decision" in line]
                print(f"   📚 Archived log ({archived_name}): {len(pre_rotation_msgs)} key messages from previous hour")
        except Exception as e:
            print(f"   ❌ Error reading archived log: {e}")
    
    # Check current log
    if os.path.exists(current_log):
        try:
            with open(current_log, 'r') as f:
                lines = f.readlines()
                post_rotation_msgs = [line for line in lines if "New hour started" in line or "fresh log" in line]
                print(f"   📝 Current log (TradeBot.log): {len(post_rotation_msgs)} messages from new hour")
        except Exception as e:
            print(f"   ❌ Error reading current log: {e}")
    
    print(f"\n🎉 Demonstration Complete!")
    print(f"\n💡 Key Benefits:")
    print(f"   • Simple monitoring: Always check 'TradeBot.log' for current activity")
    print(f"   • Historical analysis: Archived logs organized by hour")
    print(f"   • Clean separation: Each hour gets its own complete log file")
    print(f"   • Automatic management: No manual intervention required")
    print(f"   • Easy debugging: Find issues by hour timestamp")

if __name__ == "__main__":
    try:
        demonstrate_hourly_rotation()
    except Exception as e:
        print(f"\n💥 Demonstration failed: {e}")
        import traceback
        traceback.print_exc()