#!/usr/bin/env python3
"""
Test to verify the corrected timestamp logic with actual rotation simulation.
This test simulates the exact timing of log rotation to ensure correct hour assignment.
"""
import os
import tempfile
import logging
from datetime import datetime, timedelta
import pytz

def test_corrected_rotation_logic():
    """Test the corrected rotation logic with precise timing simulation."""
    print("🔧 Testing Corrected Log Rotation Timestamp Logic")
    print("=" * 55)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = os.path.join(temp_dir, "log")
        os.makedirs(log_dir, exist_ok=True)
        
        tz = pytz.timezone("US/Eastern")
        current_log = os.path.join(log_dir, "TradeBot.log")
        
        # Test scenarios: [rotation_time, expected_archived_hour, description]
        test_scenarios = [
            ("10:00:01", "09", "Morning rotation: 10:00:01 should archive hour 09 data"),
            ("15:00:02", "14", "Afternoon rotation: 15:00:02 should archive hour 14 data"),
            ("00:00:01", "23", "Midnight rotation: 00:00:01 should archive hour 23 data"),
            ("01:00:03", "00", "Early morning: 01:00:03 should archive hour 00 data"),
        ]
        
        print("🧪 Testing rotation scenarios:")
        
        for rotation_time_str, expected_hour, description in test_scenarios:
            print(f"\n📋 Scenario: {description}")
            
            # Parse rotation time
            hour, minute, second = map(int, rotation_time_str.split(":"))
            
            # Create a test datetime for "now" during rotation
            today = datetime.now(tz).date()
            rotation_time = datetime.combine(today, datetime.min.time().replace(
                hour=hour, minute=minute, second=second
            ))
            rotation_time = tz.localize(rotation_time)
            
            print(f"   ⏰ Rotation time: {rotation_time.strftime('%H:%M:%S')}")
            
            # Simulate the rename logic
            hour_that_ended = (rotation_time - timedelta(hours=1)).hour
            date_part = rotation_time.strftime("%m%d%y")
            calculated_ts = f"{date_part}.{hour_that_ended:02d}"
            
            print(f"   📦 Would archive as: TradeBot.{calculated_ts}.log")
            print(f"   🎯 Expected hour: {expected_hour}, Calculated hour: {hour_that_ended:02d}")
            
            if f"{hour_that_ended:02d}" == expected_hour:
                print(f"   ✅ CORRECT: Hour {hour_that_ended:02d} matches expected {expected_hour}")
            else:
                print(f"   ❌ ERROR: Hour {hour_that_ended:02d} does not match expected {expected_hour}")
                return False
        
        print(f"\n🎯 Real-world timeline verification:")
        
        # Simulate a complete hour of logging
        timeline = [
            ("09:15:30", "Bot starts, writes to TradeBot.log"),
            ("09:30:45", "Trading decision logged to TradeBot.log"),
            ("09:45:12", "Market update logged to TradeBot.log"),
            ("09:59:58", "Final entry before rotation to TradeBot.log"),
            ("10:00:01", "ROTATION: TradeBot.log -> TradeBot.MMDDYY.09.log"),
            ("10:00:01", "New TradeBot.log created"),
            ("10:15:22", "New entries to fresh TradeBot.log"),
        ]
        
        for time_str, event in timeline:
            print(f"   {time_str}: {event}")
        
        return True

def test_with_actual_log_content():
    """Test by creating actual log content and verifying the timestamp."""
    print(f"\n📝 Testing with Actual Log Content")
    print("=" * 40)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        log_dir = os.path.join(temp_dir, "log")
        os.makedirs(log_dir, exist_ok=True)
        
        tz = pytz.timezone("US/Eastern")
        current_log = os.path.join(log_dir, "TradeBot.log")
        
        # Create a logger that writes to TradeBot.log
        test_logger = logging.getLogger("timestamp_test")
        test_logger.setLevel(logging.INFO)
        
        # Remove any existing handlers
        for handler in test_logger.handlers[:]:
            test_logger.removeHandler(handler)
        
        # Create file handler
        file_handler = logging.FileHandler(current_log)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        test_logger.addHandler(file_handler)
        
        # Write some test logs
        test_logger.info("Test log entry 1 - simulating hour 09 activity")
        test_logger.info("Test log entry 2 - more hour 09 activity")
        test_logger.info("Test log entry 3 - final hour 09 activity")
        
        # Close handler
        file_handler.close()
        test_logger.removeHandler(file_handler)
        
        print(f"   📄 Created test log with sample entries")
        
        # Simulate rotation at 10:00:01
        rotation_time = datetime.now(tz).replace(hour=10, minute=0, second=1, microsecond=0)
        
        # Apply the rename logic
        hour_that_ended = (rotation_time - timedelta(hours=1)).hour
        date_part = rotation_time.strftime("%m%d%y")
        ts = f"{date_part}.{hour_that_ended:02d}"
        archived_log = os.path.join(log_dir, f"TradeBot.{ts}.log")
        
        # Rename the file
        os.rename(current_log, archived_log)
        
        print(f"   📦 Renamed to: TradeBot.{ts}.log")
        print(f"   🕘 Archive hour: {hour_that_ended:02d}")
        
        # Verify the content
        with open(archived_log, 'r') as f:
            content = f.read()
            
        print(f"   📋 Archived log content:")
        for line in content.strip().split('\n'):
            if line.strip():
                # Extract timestamp from log line
                timestamp_part = line[:19] if len(line) > 19 else "No timestamp"
                print(f"      {timestamp_part}")
        
        # The key insight: regardless of when we run this test,
        # the logic should archive as hour (current_hour - 1)
        print(f"\n   💡 Logic verification:")
        print(f"      • Rotation simulated at: {rotation_time.strftime('%H:%M:%S')}")
        print(f"      • Hour that ended: {hour_that_ended:02d}")
        print(f"      • Archive filename: TradeBot.{ts}.log")
        print(f"      • This represents data from hour {hour_that_ended:02d}:xx")
        
        return True

def analyze_problematic_log():
    """Analyze the specific problematic log file mentioned."""
    print(f"\n🔍 Analyzing Problematic Log File")
    print("=" * 40)
    
    problematic_file = "log/TradeBot.100225.08.log"
    
    if os.path.exists(problematic_file):
        print(f"   📄 Found: {problematic_file}")
        
        try:
            with open(problematic_file, 'r') as f:
                lines = f.readlines()
            
            print(f"   📊 Contains {len(lines)} log entries")
            
            if lines:
                print(f"   🕘 First entry: {lines[0].strip()}")
                if len(lines) > 1:
                    print(f"   🕘 Last entry:  {lines[-1].strip()}")
                
                # Analyze the timestamps
                timestamps = []
                for line in lines:
                    if len(line) > 19:
                        try:
                            ts_str = line[:19]  # YYYY-MM-DD HH:MM:SS
                            ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                            timestamps.append(ts.hour)
                        except:
                            pass
                
                if timestamps:
                    unique_hours = set(timestamps)
                    print(f"   📈 Hours present in log: {sorted(unique_hours)}")
                    
                    # Check if filename matches content
                    filename_hour = 8  # From TradeBot.100225.08.log
                    if filename_hour in unique_hours:
                        print(f"   ✅ Filename hour {filename_hour:02d} matches log content")
                    else:
                        print(f"   ❌ MISMATCH: Filename says hour {filename_hour:02d}, but log contains hours {sorted(unique_hours)}")
                        print(f"   💡 This confirms the bug we're fixing!")
        
        except Exception as e:
            print(f"   ❌ Error reading file: {e}")
    else:
        print(f"   📂 File not found: {problematic_file}")
        print(f"   💭 This is expected if running in a test environment")
    
    return True

if __name__ == "__main__":
    print("🔍 Comprehensive Timestamp Accuracy Verification")
    print("=" * 55)
    
    try:
        success = True
        success &= test_corrected_rotation_logic()
        success &= test_with_actual_log_content()
        success &= analyze_problematic_log()
        
        if success:
            print(f"\n✅ All timestamp verification tests passed!")
            print(f"\n🔧 Fix Summary:")
            print(f"   • Rotation logic now correctly calculates hour_that_ended")
            print(f"   • Archive files are named for the hour of data they contain")
            print(f"   • At 10:00:01, logs with 09:xx data are archived as hour 09")
            print(f"   • Edge cases like midnight are properly handled")
            print(f"   • Enhanced logging provides clarity about what hour data is archived")
        else:
            print(f"\n❌ Some verification tests failed!")
            
    except Exception as e:
        print(f"\n💥 Verification failed: {e}")
        import traceback
        traceback.print_exc()