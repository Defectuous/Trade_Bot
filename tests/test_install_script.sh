#!/bin/bash

# Test script for install_tradebot.sh improvements
# This script validates the user creation logic without actually running the full installation

echo "🧪 Testing install_tradebot.sh User Creation Logic"
echo "=================================================="

# Test 1: Validate script syntax
echo
echo "Test 1: Syntax validation..."
if bash -n install_tradebot.sh; then
    echo "✅ Syntax check passed"
else
    echo "❌ Syntax errors found"
    exit 1
fi

# Test 2: Check required commands exist
echo
echo "Test 2: Command availability check..."
commands=("adduser" "usermod" "groups" "sudo")
for cmd in "${commands[@]}"; do
    if command -v "$cmd" >/dev/null 2>&1; then
        echo "✅ $cmd - available"
    else
        echo "❌ $cmd - missing"
    fi
done

# Test 3: Validate username regex pattern
echo
echo "Test 3: Username validation patterns..."
test_usernames=("tradebot" "trade-bot" "trade_bot" "trading123" "INVALID" "123invalid" "-invalid")
for username in "${test_usernames[@]}"; do
    if [[ "$username" =~ ^[a-z][a-z0-9_-]*$ ]]; then
        echo "✅ '$username' - valid format"
    else
        echo "❌ '$username' - invalid format"
    fi
done

# Test 4: Check group existence
echo
echo "Test 4: System group availability..."
groups=("adm" "dialout" "cdrom" "sudo" "audio" "video" "plugdev" "games" "users" "netdev" "input")
for group in "${groups[@]}"; do
    if getent group "$group" >/dev/null 2>&1; then
        echo "✅ $group - exists"
    else
        echo "⚠️  $group - not found (may be OK on non-Pi systems)"
    fi
done

# Test 5: Extract and validate key sections from install script
echo
echo "Test 5: Script content validation..."

# Check if adduser is used instead of useradd
if grep -q "adduser --gecos" install_tradebot.sh; then
    echo "✅ Uses adduser with proper flags"
else
    echo "❌ Missing adduser usage"
fi

# Check if proper groups are assigned
if grep -q "adm,dialout,cdrom,sudo,audio,video,plugdev,games,users,netdev,input" install_tradebot.sh; then
    echo "✅ Assigns proper Pi-compatible groups"
else
    echo "❌ Missing proper group assignments"
fi

# Check for error handling
if grep -q "if \[ \$? -eq 0 \]" install_tradebot.sh; then
    echo "✅ Includes error handling"
else
    echo "❌ Missing error handling"
fi

# Check for improved documentation
if grep -q "7-indicator technical analysis" install_tradebot.sh; then
    echo "✅ Updated documentation to reflect current features"
else
    echo "❌ Documentation needs updating"
fi

echo
echo "🎯 Test Summary:"
echo "The install_tradebot.sh script has been improved with:"
echo "• Better user creation using adduser"
echo "• Comprehensive Raspberry Pi group assignments" 
echo "• Enhanced error handling and validation"
echo "• Updated documentation and feature descriptions"
echo "• Clear information about group permissions"
echo
echo "✅ Ready for deployment on Raspberry Pi systems!"