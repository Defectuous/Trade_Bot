#!/bin/bash

# Create TradeBot User Script
# This script creates the 'tradebot' user with proper permissions
# Run this BEFORE running the main install_tradebot.sh script
#
# Usage: curl -sSL https://raw.githubusercontent.com/Defectuous/Trade_Bot/main/create_tradebot_user.sh | bash

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print status messages
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

echo -e "${BLUE}🔧 TradeBot User Creation Script${NC}"
echo -e "${BLUE}================================${NC}"
echo -e "${YELLOW}This script will create the 'tradebot' user for running the trading bot${NC}"
echo

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run this script as root (don't use sudo)"
    print_info "The script will prompt for sudo when needed"
    exit 1
fi

# Check if user already exists
if id "tradebot" &>/dev/null; then
    print_warning "User 'tradebot' already exists"
    echo -e "${BLUE}Existing user information:${NC}"
    id "tradebot"
    echo
    
    # Check if user has sudo privileges
    if sudo -l -U tradebot 2>/dev/null | grep -q "(ALL)"; then
        print_status "User 'tradebot' already has sudo privileges"
        echo -e "${GREEN}✅ User setup is complete!${NC}"
        echo
        echo -e "${YELLOW}Next step: Run the main installation script:${NC}"
        echo "curl -sSL https://raw.githubusercontent.com/Defectuous/Trade_Bot/main/install_tradebot.sh | bash"
        exit 0
    else
        print_warning "User 'tradebot' exists but may not have sudo privileges"
        read -p "Add sudo privileges to existing user? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Adding sudo privileges to existing user 'tradebot'..."
            sudo usermod -a -G sudo tradebot
            print_status "Sudo privileges added successfully"
            echo
            echo -e "${GREEN}✅ User setup is complete!${NC}"
            echo
            echo -e "${YELLOW}Next step: Run the main installation script:${NC}"
            echo "curl -sSL https://raw.githubusercontent.com/Defectuous/Trade_Bot/main/install_tradebot.sh | bash"
            exit 0
        else
            print_info "Exiting without changes"
            exit 0
        fi
    fi
fi

# Create the tradebot user
print_info "Creating user 'tradebot'..."
echo -e "${BLUE}You will be prompted to:${NC}"
echo "• Set a password for the tradebot user"
echo "• Optionally fill in user details (you can press Enter to skip)"
echo

# Use adduser for interactive setup
sudo adduser tradebot

if [ $? -eq 0 ]; then
    print_status "User 'tradebot' created successfully"
    
    # Add user to sudo group
    print_info "Adding user to sudo group..."
    sudo usermod -a -G sudo tradebot
    
    if [ $? -eq 0 ]; then
        print_status "User added to sudo group successfully"
        
        # Verify the setup
        echo
        echo -e "${BLUE}User Information:${NC}"
        id tradebot
        echo
        echo -e "${BLUE}Groups:${NC}"
        groups tradebot
        
        echo
        print_status "User 'tradebot' is ready!"
        
        echo
        echo -e "${GREEN}✅ User setup is complete!${NC}"
        echo
        echo -e "${YELLOW}Next step: Run the main installation script:${NC}"
        echo "curl -sSL https://raw.githubusercontent.com/Defectuous/Trade_Bot/main/install_tradebot.sh | bash"
        
    else
        print_error "Failed to add user to sudo group"
        print_info "You can manually add sudo privileges later with:"
        print_info "sudo usermod -a -G sudo tradebot"
        exit 1
    fi
else
    print_error "Failed to create user 'tradebot'"
    exit 1
fi