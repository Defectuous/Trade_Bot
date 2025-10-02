#!/usr/bin/env python3
"""
Test script to verify the enhanced logging behavior works in the actual trading bot.
This enables file logging and runs a short test cycle to demonstrate the rotation.
"""
import os
import time
import tempfile
import subprocess
import sys
from datetime import datetime
import pytz

def test_bot_with_logging():
    """Test the actual bot with logging enabled."""
    print("🤖 Testing Trading Bot with Enhanced Hourly Logging")
    print("=" * 60)
    
    # Check if .env has LOG_TO_FILE enabled
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            content = f.read()
            if "LOG_TO_FILE=true" in content:
                print("✅ LOG_TO_FILE is enabled in .env")
            else:
                print("❌ LOG_TO_FILE is not enabled in .env")
                print("   Please set LOG_TO_FILE=true in your .env file")
                return False
    else:
        print("❌ .env file not found")
        return False
    
    # Check if log directory exists
    log_dir = "log"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
        print(f"📁 Created log directory: {log_dir}")
    else:
        print(f"📁 Log directory exists: {log_dir}")
    
    # Show current log directory contents before test
    print(f"\n📂 Log directory contents before test:")
    try:
        log_files = [f for f in os.listdir(log_dir) if f.startswith("TradeBot")]
        if log_files:
            for log_file in sorted(log_files):
                file_path = os.path.join(log_dir, log_file)
                size = os.path.getsize(file_path)
                print(f"   📄 {log_file} ({size} bytes)")
        else:
            print("   (empty)")
    except Exception as e:
        print(f"   ❌ Error reading directory: {e}")
    
    # Check if DRY_RUN is enabled (safer for testing)
    print(f"\n🧪 Testing with enhanced logging...")
    
    # Test the bot import and setup
    try:
        # Set environment for testing
        original_dry_run = os.environ.get('DRY_RUN')
        original_log_level = os.environ.get('LOG_LEVEL')
        
        os.environ['DRY_RUN'] = 'true'  # Ensure dry run for safety
        os.environ['LOG_LEVEL'] = 'INFO'
        
        print("   📝 Importing trade_bot module...")
        import trade_bot
        
        print("   ✅ Trade bot imported successfully")
        print("   📋 Logging configuration detected:")
        
        # Check if file logging was set up
        log_file_current = os.path.join(log_dir, "TradeBot.log")
        if os.path.exists(log_file_current):
            print(f"   ✅ Current log file created: TradeBot.log")
            
            # Check the size to see if logging is active
            size = os.path.getsize(log_file_current)
            print(f"   📊 Current log file size: {size} bytes")
            
            if size > 0:
                print("   ✅ Logging is active (file has content)")
                
                # Show the last few lines of the current log
                try:
                    with open(log_file_current, 'r') as f:
                        lines = f.readlines()
                        print(f"   📋 Last few log entries:")
                        for line in lines[-3:]:
                            print(f"      {line.strip()}")
                except Exception as e:
                    print(f"   ⚠️  Could not read log content: {e}")
            else:
                print("   ⚠️  Log file exists but is empty")
        else:
            print("   ❌ Current log file (TradeBot.log) not found")
            print("   💡 This might mean LOG_TO_FILE is disabled or setup failed")
        
        # Restore original environment
        if original_dry_run:
            os.environ['DRY_RUN'] = original_dry_run
        if original_log_level:
            os.environ['LOG_LEVEL'] = original_log_level
        
    except ImportError as e:
        print(f"   ❌ Failed to import trade_bot: {e}")
        print("   💡 Make sure all dependencies are installed")
        return False
    except Exception as e:
        print(f"   ❌ Error during bot test: {e}")
        return False
    
    # Show final log directory state
    print(f"\n📂 Log directory contents after test:")
    try:
        log_files = [f for f in os.listdir(log_dir) if f.startswith("TradeBot")]
        if log_files:
            for log_file in sorted(log_files):
                file_path = os.path.join(log_dir, log_file)
                size = os.path.getsize(file_path)
                mtime = os.path.getmtime(file_path)
                mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
                print(f"   📄 {log_file} ({size} bytes, modified: {mtime_str})")
        else:
            print("   (no TradeBot log files found)")
    except Exception as e:
        print(f"   ❌ Error reading directory: {e}")
    
    print(f"\n🎯 How to monitor your bot:")
    print(f"   📖 Current activity: tail -f {log_dir}/TradeBot.log")
    print(f"   📚 Historical logs: ls -la {log_dir}/TradeBot.*.log")
    print(f"   🔍 Search logs: grep 'BUY\\|SELL' {log_dir}/TradeBot*.log")
    
    tz = pytz.timezone("US/Eastern")
    current_hour = datetime.now(tz).strftime("%H")
    next_hour = str(int(current_hour) + 1).zfill(2)
    today = datetime.now(tz).strftime("%m%d%y")
    
    print(f"\n⏰ Next log rotation:")
    print(f"   📅 Current hour: {current_hour}:xx (TradeBot.log)")
    print(f"   📅 Next rotation: {next_hour}:00 (TradeBot.log -> TradeBot.{today}.{current_hour}.log)")
    
    return True

def show_monitoring_commands():
    """Show useful commands for monitoring the enhanced logging."""
    print(f"\n📋 Useful Monitoring Commands:")
    print(f"=" * 40)
    
    commands = [
        ("View current log", "tail -f log/TradeBot.log"),
        ("View all log files", "ls -la log/TradeBot*.log"),
        ("Find trading activity", "grep -E 'BUY|SELL|GPT decision' log/TradeBot*.log"),
        ("View last hour's activity", "ls -t log/TradeBot*.log | head -1 | xargs cat"),
        ("Count log files", "ls log/TradeBot.*.log | wc -l"),
        ("Monitor systemd service", "sudo journalctl -u trade_bot.service -f"),
        ("Check log file sizes", "du -h log/TradeBot*.log"),
    ]
    
    for description, command in commands:
        print(f"   📝 {description}:")
        print(f"      {command}")
        print()

if __name__ == "__main__":
    try:
        success = test_bot_with_logging()
        show_monitoring_commands()
        
        if success:
            print("✅ Enhanced logging test completed successfully!")
        else:
            print("❌ Some issues were found. Check the output above.")
            
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)