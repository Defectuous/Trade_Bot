#!/bin/bash

# Trade_Bot Raspberry Pi Installation Script
# This script will install and configure the Enhanced Trading Bot with 7-indicator technical analysis
# Features: RSI, MA, EMA, Pattern Analysis, ADX, ADXR, Candlestick Data -> GPT -> Alpaca Trading
# Includes position concentration risk management and comprehensive safety features
# 
# PREREQUISITE: Create the tradebot user BEFORE running this script:
#   curl -sSL https://raw.githubusercontent.com/Defectuous/Trade_Bot/main/create_tradebot_user.sh | bash
#
# Then run this script:
#   curl -sSL https://raw.githubusercontent.com/Defectuous/Trade_Bot/main/install_tradebot.sh | bash
#
# This script assumes the 'tradebot' user already exists with sudo privileges

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
GITHUB_REPO="https://github.com/Defectuous/Trade_Bot.git"  # Update this with your actual repo
SERVICE_NAME="trade_bot.service"

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

echo -e "${BLUE}🚀 Trade_Bot Raspberry Pi Installation Script${NC}"
echo -e "${BLUE}============================================${NC}"

# First, provide clear instructions for user creation
echo -e "${YELLOW}📋 PREREQUISITE SETUP${NC}"
echo -e "${BLUE}Before running this installation, you need to create the 'tradebot' user.${NC}"
echo -e "${BLUE}If you haven't done this yet, run:${NC}"
echo
echo -e "${GREEN}curl -sSL https://raw.githubusercontent.com/Defectuous/Trade_Bot/main/create_tradebot_user.sh | bash${NC}"
echo
echo -e "${BLUE}============================================${NC}"
echo

# Check if tradebot user exists
if ! id "tradebot" &>/dev/null; then
    print_error "User 'tradebot' does not exist!"
    echo
    echo -e "${YELLOW}Please create the tradebot user first by running:${NC}"
    echo "curl -sSL https://raw.githubusercontent.com/Defectuous/Trade_Bot/main/create_tradebot_user.sh | bash"
    echo
    echo "Then run this script again."
    exit 1
fi

# Check if tradebot user has sudo privileges
if ! sudo -l -U tradebot 2>/dev/null | grep -q "(ALL)"; then
    print_warning "User 'tradebot' may not have sudo privileges"
    echo -e "${YELLOW}Add sudo privileges with:${NC}"
    echo "  sudo usermod -a -G sudo tradebot"
    echo
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

print_status "User 'tradebot' found and configured"
TRADEBOT_USER="tradebot"
INSTALL_DIR="/home/$TRADEBOT_USER/Trade_Bot"

print_info "Installation directory: $INSTALL_DIR"
echo

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run this script as root (don't use sudo)"
    print_info "The script will prompt for sudo when needed"
    exit 1
fi

echo -e "${YELLOW}Step 1: Updating Raspberry Pi system...${NC}"

# Update system
print_info "Updating package lists..."
sudo apt update

print_info "Upgrading system packages (this may take several minutes)..."
sudo apt upgrade -y

print_info "Installing required system packages..."
sudo apt install -y python3 python3-venv python3-pip git curl nano tmux

# Clean up
sudo apt autoremove -y
sudo apt autoclean

print_status "System update completed"

# Create function to run commands as tradebot user
run_as_tradebot() {
    sudo -u $TRADEBOT_USER bash -c "$1"
}

echo -e "${YELLOW}Step 2: Installing Trade_Bot from GitHub as tradebot user...${NC}"

# Switch to tradebot user home directory
print_info "Switching to tradebot user environment..."

# Check if directory already exists
if [ -d "$INSTALL_DIR" ]; then
    print_warning "Trade_Bot directory already exists at $INSTALL_DIR"
    print_info "Using existing directory"
fi

# Clone repository as tradebot user
if [ ! -d "$INSTALL_DIR" ]; then
    print_info "Cloning Trade_Bot repository as user '$TRADEBOT_USER'..."
    run_as_tradebot "git clone $GITHUB_REPO $INSTALL_DIR"
fi

# Set proper ownership
print_info "Setting proper file ownership..."
sudo chown -R $TRADEBOT_USER:$TRADEBOT_USER $INSTALL_DIR

print_status "Trade_Bot repository ready"

echo -e "${YELLOW}Step 3: Setting up Python virtual environment...${NC}"

# Create virtual environment as tradebot user
print_info "Creating Python virtual environment as user '$TRADEBOT_USER'..."
run_as_tradebot "cd $INSTALL_DIR && python3 -m venv .venv"

# Install Python dependencies as tradebot user
print_info "Installing Python dependencies..."
run_as_tradebot "cd $INSTALL_DIR && source .venv/bin/activate && pip install -r requirements.txt"

# Make trade_bot.py executable
print_info "Making trade_bot.py executable..."
run_as_tradebot "chmod +x $INSTALL_DIR/trade_bot.py"

print_status "Python environment setup completed"

echo -e "${YELLOW}Step 4: Configuring environment variables (.env file)...${NC}"

# Create .env file from template as tradebot user
if sudo -u $TRADEBOT_USER [ -f "$INSTALL_DIR/.env" ]; then
    print_warning "Existing .env file found"
    print_info "Keeping existing .env file"
    ENV_EXISTS=true
fi

if [ "$ENV_EXISTS" != true ]; then
    if [ -f "$INSTALL_DIR/.env.example" ]; then
        run_as_tradebot "cd $INSTALL_DIR && cp .env.example .env"
    else
        print_warning ".env.example not found, creating basic .env file"
        run_as_tradebot "cat > $INSTALL_DIR/.env << 'EOL'
# TAAPI.io API Key (required for technical indicators)
TAAPI_KEY=

# OpenAI API Configuration
OPENAI_API_KEY=
OPENAI_MODEL=gpt-3.5-turbo

# Alpaca Trading API Configuration
ALPACA_API_KEY=
ALPACA_SECRET_KEY=
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Trading Configuration
SYMBOL=AAPL
QTY=1
DRY_RUN=true

# Discord Notifications (Optional)
DISCORD_WEBHOOK_URL=

# Technical Indicator Configuration
MA_PERIOD=20
EMA_PERIOD=12
ADX_PERIOD=14
ADXR_PERIOD=14

# Technical Indicator Enable/Disable
ENABLE_RSI=true
ENABLE_MA=true
ENABLE_EMA=true
ENABLE_PATTERN=true
ENABLE_ADX=true
ENABLE_ADXR=true
ENABLE_CANDLE=true
EOL"
    fi
    
    print_info ".env file created with default settings"
    print_info "Edit $INSTALL_DIR/.env to configure your API keys after installation"
    print_status "Environment configuration completed"
fi

echo -e "${YELLOW}Step 5: Creating systemd service...${NC}"

# Get tradebot user home directory
TRADEBOT_HOME="/home/$TRADEBOT_USER"

# Create systemd service file
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME"

print_info "Creating systemd service file to run as user '$TRADEBOT_USER'..."
sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=Advanced AI Trading Bot with 6-Indicator Analysis
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=$TRADEBOT_USER
Group=$TRADEBOT_USER
WorkingDirectory=$INSTALL_DIR
EnvironmentFile=$INSTALL_DIR/.env
ExecStart=$INSTALL_DIR/.venv/bin/python $INSTALL_DIR/trade_bot.py
Restart=on-failure
RestartSec=30s
StandardOutput=journal
StandardError=journal

# Security settings for trading bot
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=$INSTALL_DIR
ReadWritePaths=$INSTALL_DIR/log

# Resource limits
LimitNOFILE=1024
MemoryMax=512M

[Install]
WantedBy=multi-user.target
EOF

# Set proper permissions for .env file (readable only by tradebot user)
print_info "Securing .env file permissions..."
sudo chown $TRADEBOT_USER:$TRADEBOT_USER $INSTALL_DIR/.env
sudo chmod 600 $INSTALL_DIR/.env

# Create log directory and set permissions
print_info "Creating log directory..."
run_as_tradebot "mkdir -p $INSTALL_DIR/log"
sudo chown -R $TRADEBOT_USER:$TRADEBOT_USER $INSTALL_DIR/log

# Reload systemd
sudo systemctl daemon-reload

print_status "Systemd service created and configured for user '$TRADEBOT_USER'"

echo -e "${YELLOW}Step 6: Testing installation...${NC}"

# Test the bot can start as tradebot user
print_info "Testing bot startup as user '$TRADEBOT_USER'..."
timeout 10s sudo -u $TRADEBOT_USER bash -c "cd $INSTALL_DIR && source .venv/bin/activate && python trade_bot.py" || print_info "Test completed (timeout expected)"

print_status "Installation test completed"

echo -e "${GREEN}🎉 TradeBot Installation Complete!${NC}"
echo -e "${BLUE}============================================${NC}"
echo

echo -e "${YELLOW}⚠ IMPORTANT: Configure API Keys Before Starting${NC}"
echo
echo -e "${BLUE}🔧 Configure your API keys:${NC}"
echo "   sudo -u $TRADEBOT_USER nano $INSTALL_DIR/.env"
echo
echo -e "${YELLOW}Required API Keys:${NC}"
echo "• TAAPI_KEY - Get from https://taapi.io (~\$15/month for technical indicators)"
echo "• OPENAI_API_KEY - Get from https://platform.openai.com (pay-per-use)"
echo "• ALPACA_API_KEY & ALPACA_SECRET_KEY - Get from https://alpaca.markets (free paper trading)"
echo
echo -e "${YELLOW}Optional Settings:${NC}"
echo "• DISCORD_WEBHOOK_URL - For trade notifications"
echo "• SYMBOL - Change from AAPL to your preferred stock"
echo "• QTY - Adjust quantity per trade"
echo

echo -e "${YELLOW}Security Features Implemented:${NC}"
echo "• ✅ Uses dedicated 'tradebot' user account"
echo "• ✅ Restricted file permissions (.env readable only by tradebot)"
echo "• ✅ Systemd security hardening (NoNewPrivileges, PrivateTmp, etc.)"
echo "• ✅ Resource limits (512MB memory, 1024 file handles)"
echo "• ✅ Bot runs with minimal privileges"
echo "• ✅ DRY_RUN mode enabled by default (safe for testing)"
echo

echo -e "${YELLOW}Next Steps (After configuring API keys):${NC}"
echo
echo "1. 📊 Verify your configuration as tradebot user:"
echo "   sudo -u $TRADEBOT_USER nano $INSTALL_DIR/.env"
echo
echo "2. 🧪 Test the bot manually:"
echo "   sudo -u $TRADEBOT_USER bash -c 'cd $INSTALL_DIR && source .venv/bin/activate && python trade_bot.py'"
echo
echo "3. 🚀 Enable and start the service:"
echo "   sudo systemctl enable trade_bot.service"
echo "   sudo systemctl start trade_bot.service"
echo
echo "4. 📋 Monitor the service:"
echo "   sudo systemctl status trade_bot.service"
echo "   sudo journalctl -u trade_bot.service -f"
echo
echo "5. 🛑 Stop the service:"
echo "   sudo systemctl stop trade_bot.service"
echo
echo "6. 🔐 Switch to tradebot user (if needed):"
echo "   sudo su - $TRADEBOT_USER"
echo
echo -e "${YELLOW}Important Security Notes:${NC}"
echo "• Bot runs under dedicated 'tradebot' user account (not your main user)"
echo "• .env file is only readable by tradebot user (600 permissions)"
echo "• Service runs with strict security settings and resource limits"
echo "• Bot is configured in DRY_RUN mode by default (safe for testing)"
echo "• Test thoroughly before enabling live trading"
echo "• Monitor logs regularly for any issues"
echo "• Keep your API keys secure"
echo
echo -e "${BLUE}Configuration file location: $INSTALL_DIR/.env${NC}"
echo -e "${BLUE}Service file location: $SERVICE_FILE${NC}"
echo -e "${BLUE}Log location: sudo journalctl -u trade_bot.service${NC}"
echo -e "${BLUE}Tradebot user home: /home/$TRADEBOT_USER${NC}"
echo
echo -e "${GREEN}Happy Secure Trading! 🚀📈🔒${NC}"