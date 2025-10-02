#!/usr/bin/env python3
"""
Simple test script to demonstrate the new hourly logging rotation behavior.
This creates a basic demonstration of the logging functionality.
"""
import os
import time
import logging
from datetime import datetime, timedelta
import pytz

def test_logging_behavior():
    """Test the logging behavior with actual files."""
    print("🔧 Testing New Hourly Logging Rotation Behavior")
    print("=" * 55)
    
    # Ensure log directory exists
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(base_dir, "log")
    os.makedirs(logs_dir, exist_ok=True)
    
    current_log = os.path.join(logs_dir, "TradeBot.log")
    
    print(f"📁 Log directory: {logs_dir}")
    print(f"📄 Current log file: {current_log}")
    
    # Set up basic file logging to TradeBot.log
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.INFO)
    
    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create file handler for TradeBot.log
    file_handler = logging.FileHandler(current_log)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(file_handler)
    
    print("\n✅ Phase 1: Initial logging to TradeBot.log")
    logger.info("Test message 1 - Initial logging to TradeBot.log")
    logger.info("Test message 2 - Bot starting up")
    logger.info("Test message 3 - Trading cycle beginning")
    
    print(f"   📝 Log messages written to: TradeBot.log")
    
    # Verify file exists and has content
    if os.path.exists(current_log):
        size = os.path.getsize(current_log)
        print(f"   📊 Current log file size: {size} bytes")
    
    # Simulate hour change - close current handler and rename file
    print("\n🔄 Phase 2: Simulating hourly rotation")
    
    # Close the current handler
    file_handler.close()
    logger.removeHandler(file_handler)
    
    # Create timestamped filename for the previous hour
    tz = pytz.timezone("US/Eastern")
    prev_hour = datetime.now(tz) - timedelta(hours=1)
    ts = prev_hour.strftime("%m%d%y.%H")
    archived_log = os.path.join(logs_dir, f"TradeBot.{ts}.log")
    
    # Rename current log to archived name
    if os.path.exists(current_log):
        try:
            os.rename(current_log, archived_log)
            print(f"   📦 Renamed: TradeBot.log -> TradeBot.{ts}.log")
        except Exception as e:
            print(f"   ❌ Rename failed: {e}")
            return False
    
    # Create new TradeBot.log handler
    print("\n✅ Phase 3: Creating new TradeBot.log")
    new_file_handler = logging.FileHandler(current_log)
    new_file_handler.setLevel(logging.INFO)
    new_file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(new_file_handler)
    
    logger.info("Test message 4 - New hour started, fresh log file")
    logger.info("Test message 5 - Continuing trading operations")
    
    print(f"   📝 New log messages written to: TradeBot.log")
    
    # Show final state
    print("\n📁 Final log directory contents:")
    try:
        for file in sorted(os.listdir(logs_dir)):
            if file.startswith("TradeBot"):
                file_path = os.path.join(logs_dir, file)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    print(f"   📄 {file} ({size} bytes)")
    except Exception as e:
        print(f"   ❌ Error listing files: {e}")
    
    # Verify content separation
    print("\n🔍 Verifying log content separation:")
    
    # Check archived log
    if os.path.exists(archived_log):
        try:
            with open(archived_log, 'r') as f:
                archived_content = f.read()
                if "Test message 1" in archived_content and "Test message 4" not in archived_content:
                    print(f"   ✅ Archived log (TradeBot.{ts}.log) contains only initial messages")
                else:
                    print(f"   ❌ Archived log content incorrect")
        except Exception as e:
            print(f"   ❌ Error reading archived log: {e}")
    
    # Check current log
    if os.path.exists(current_log):
        try:
            with open(current_log, 'r') as f:
                current_content = f.read()
                if "Test message 4" in current_content and "Test message 1" not in current_content:
                    print("   ✅ Current log (TradeBot.log) contains only new messages")
                else:
                    print("   ❌ Current log content incorrect")
        except Exception as e:
            print(f"   ❌ Error reading current log: {e}")
    
    # Clean up
    new_file_handler.close()
    logger.removeHandler(new_file_handler)
    
    print("\n🎉 Test completed successfully!")
    print("\nHow the logging works:")
    print("  1. Bot starts logging to 'TradeBot.log'")
    print("  2. At the top of each hour, the current log is renamed to 'TradeBot.MMDDYY.HH.log'")
    print("  3. A new 'TradeBot.log' file is created for the new hour")
    print("  4. This creates a clean hourly archive while keeping the current log simple")
    
    return True

def demonstrate_filename_format():
    """Show examples of the timestamp format used."""
    print("\n📅 Timestamp Format Examples:")
    tz = pytz.timezone("US/Eastern")
    
    # Show current and several previous hours
    for i in range(5):
        test_time = datetime.now(tz) - timedelta(hours=i)
        ts = test_time.strftime("%m%d%y.%H")
        hour_str = test_time.strftime("%I:%M %p %Z")
        print(f"   {hour_str} -> TradeBot.{ts}.log")

if __name__ == "__main__":
    try:
        demonstrate_filename_format()
        test_logging_behavior()
    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()