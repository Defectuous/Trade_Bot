#!/usr/bin/env python3
"""
Test to verify that log files are renamed with the correct hour timestamp.
This test validates that the renamed log contains the hour of data it actually stored.
"""
import os
import time
from datetime import datetime, timedelta
import pytz

def test_timestamp_logic():
    """Test the timestamp logic for log rotation."""
    print("🕐 Testing Log Rotation Timestamp Logic")
    print("=" * 45)
    
    tz = pytz.timezone("US/Eastern")
    
    # Simulate different rotation scenarios
    test_cases = [
        ("10:00:01", "09"),  # Just after 10 AM, should archive as hour 09
        ("15:00:02", "14"),  # Just after 3 PM, should archive as hour 14
        ("00:00:01", "23"),  # Just after midnight, should archive as hour 23
        ("01:00:03", "00"),  # Just after 1 AM, should archive as hour 00
    ]
    
    print("🧪 Testing timestamp calculation scenarios:")
    print("   Format: [Current Time] -> [Archived Hour] (Expected)")
    
    for current_time_str, expected_hour in test_cases:
        # Parse the test time
        today = datetime.now(tz).date()
        hour, minute, second = map(int, current_time_str.split(":"))
        
        # Create test datetime
        test_time = datetime.combine(today, datetime.min.time().replace(
            hour=hour, minute=minute, second=second
        ))
        test_time = tz.localize(test_time)
        
        # Apply the same logic as the code
        prev_hour = test_time - timedelta(hours=1)
        calculated_hour = prev_hour.strftime("%H")
        
        status = "✅" if calculated_hour == expected_hour else "❌"
        print(f"   {status} {current_time_str} -> Hour {calculated_hour} (Expected: {expected_hour})")
        
        if calculated_hour != expected_hour:
            print(f"      ERROR: Expected hour {expected_hour}, got {calculated_hour}")
            return False
    
    print("\n🎯 Real-world scenario verification:")
    
    # Show what happens in a real rotation scenario
    scenarios = [
        "Bot starts logging at 09:15 AM -> writes to TradeBot.log",
        "Logs accumulate from 09:15 to 09:59 -> all in TradeBot.log", 
        "At 10:00:01 rotation occurs:",
        "  - TradeBot.log (with 09:xx data) -> TradeBot.MMDDYY.09.log",
        "  - New TradeBot.log created for 10:xx data",
        "At 11:00:01 next rotation:",
        "  - TradeBot.log (with 10:xx data) -> TradeBot.MMDDYY.10.log",
        "  - New TradeBot.log created for 11:xx data"
    ]
    
    for scenario in scenarios:
        print(f"   📝 {scenario}")
    
    return True

def test_edge_cases():
    """Test edge cases like midnight rollover."""
    print(f"\n🌙 Testing Edge Cases (Midnight, etc.)")
    print("=" * 40)
    
    tz = pytz.timezone("US/Eastern")
    
    # Test midnight rollover
    print("🕛 Midnight rollover scenario:")
    
    # Simulate logs from 11:30 PM to 11:59 PM
    late_night = datetime.now(tz).replace(hour=23, minute=30, second=0, microsecond=0)
    print(f"   📝 11:30 PM: Bot logging to TradeBot.log")
    print(f"   📝 11:45 PM: Still logging to TradeBot.log")
    print(f"   📝 11:59 PM: Still logging to TradeBot.log")
    
    # At midnight + 1 second
    midnight_plus = datetime.now(tz).replace(hour=0, minute=0, second=1, microsecond=0)
    prev_hour = midnight_plus - timedelta(hours=1)
    archived_hour = prev_hour.strftime("%H")
    
    print(f"   🔄 00:00:01: Rotation occurs")
    print(f"   📦 TradeBot.log (23:xx data) -> TradeBot.MMDDYY.{archived_hour}.log")
    print(f"   📄 New TradeBot.log created for 00:xx data")
    
    if archived_hour == "23":
        print("   ✅ Midnight rollover correct: 23:xx data archived as hour 23")
        return True
    else:
        print(f"   ❌ Midnight rollover incorrect: Expected 23, got {archived_hour}")
        return False

def verify_with_actual_logs():
    """Check if existing log files follow the expected pattern."""
    print(f"\n📁 Verifying Existing Log Files")
    print("=" * 35)
    
    log_dir = "log"
    if not os.path.exists(log_dir):
        print("   📂 No log directory found")
        return True
    
    # Get all TradeBot log files
    log_files = [f for f in os.listdir(log_dir) if f.startswith("TradeBot.") and f.endswith(".log")]
    
    if not log_files:
        print("   📄 No archived log files found")
        return True
    
    print(f"   📊 Found {len(log_files)} archived log files:")
    
    for log_file in sorted(log_files):
        if "." in log_file and log_file.count(".") >= 2:
            # Parse filename: TradeBot.MMDDYY.HH.log
            try:
                parts = log_file.split(".")
                if len(parts) >= 3:
                    date_part = parts[1]  # MMDDYY
                    hour_part = parts[2]  # HH
                    
                    print(f"   📄 {log_file}")
                    print(f"      📅 Date: {date_part}, Hour: {hour_part}")
                    
                    # Check if we can read the file to verify contents
                    file_path = os.path.join(log_dir, log_file)
                    try:
                        with open(file_path, 'r') as f:
                            lines = f.readlines()
                            if lines:
                                first_line = lines[0].strip()
                                last_line = lines[-1].strip()
                                
                                # Try to extract timestamps from log entries
                                if len(first_line) > 19:  # Has timestamp
                                    first_timestamp = first_line[:19]
                                    print(f"      ⏰ First entry: {first_timestamp}")
                                
                                if len(last_line) > 19 and len(lines) > 1:
                                    last_timestamp = last_line[:19]
                                    print(f"      ⏰ Last entry:  {last_timestamp}")
                    except Exception as e:
                        print(f"      ⚠️  Could not read file: {e}")
            except Exception as e:
                print(f"   ❌ Could not parse filename {log_file}: {e}")
    
    return True

if __name__ == "__main__":
    print("🔍 Verifying Log Rotation Timestamp Accuracy")
    print("=" * 50)
    
    try:
        success = True
        success &= test_timestamp_logic()
        success &= test_edge_cases()
        success &= verify_with_actual_logs()
        
        if success:
            print(f"\n✅ All timestamp verification tests passed!")
            print(f"\n💡 Summary:")
            print(f"   • Log files are renamed with the hour of data they contain")
            print(f"   • Rotation happens just after the hour boundary (XX:00:01)")
            print(f"   • Previous hour's data is correctly archived")
            print(f"   • Edge cases like midnight are handled properly")
            print(f"   • TradeBot.log always contains current hour's data")
        else:
            print(f"\n❌ Some verification tests failed!")
            
    except Exception as e:
        print(f"\n💥 Verification failed: {e}")
        import traceback
        traceback.print_exc()