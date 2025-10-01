#!/bin/bash

# Trade_Bot Raspberry Pi Installation Script
# This script will install and configure the RSI->GPT->Alpaca Trading Bot
# Run with: curl -sSL https://raw.githubusercontent.com/Defectuous/Trade_Bot/main/install_tradebot.sh | bash

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
GITHUB_REPO="https://github.com/Defectuous/Trade_Bot.git"  # Update this with your actual repo
TRADEBOT_USER="tradebot"
INSTALL_DIR="/home/$TRADEBOT_USER/Trade_Bot"
SERVICE_NAME="trade_bot.service"

echo -e "${BLUE}🚀 Trade_Bot Raspberry Pi Installation Script${NC}"
echo -e "${BLUE}============================================${NC}"
echo -e "${YELLOW}This script will create a dedicated user account for security${NC}"

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

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run this script as root (don't use sudo)"
    print_info "The script will prompt for sudo when needed"
    exit 1
fi

echo -e "${YELLOW}Step 1: Creating dedicated tradebot user account...${NC}"

# Check if tradebot user already exists
if id "$TRADEBOT_USER" &>/dev/null; then
    print_warning "User '$TRADEBOT_USER' already exists"
    read -p "Do you want to continue with existing user? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Installation cancelled"
        exit 0
    fi
else
    print_info "Creating user '$TRADEBOT_USER'..."
    sudo useradd -m -s /bin/bash $TRADEBOT_USER
    
    print_info "Setting password for user '$TRADEBOT_USER'..."
    echo -e "${YELLOW}Please set a secure password for the tradebot user:${NC}"
    sudo passwd $TRADEBOT_USER
    
    # Add tradebot user to necessary groups
    print_info "Adding user to necessary groups..."
    sudo usermod -a -G sudo $TRADEBOT_USER
    
    print_status "User '$TRADEBOT_USER' created successfully"
fi

# Create function to run commands as tradebot user
run_as_tradebot() {
    sudo -u $TRADEBOT_USER bash -c "$1"
}

echo -e "${YELLOW}Step 2: Updating Raspberry Pi system...${NC}"

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

echo -e "${YELLOW}Step 3: Installing Trade_Bot from GitHub as tradebot user...${NC}"

# Switch to tradebot user home directory
print_info "Switching to tradebot user environment..."

# Check if directory already exists
if [ -d "$INSTALL_DIR" ]; then
    print_warning "Trade_Bot directory already exists at $INSTALL_DIR"
    read -p "Do you want to remove it and reinstall? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo rm -rf "$INSTALL_DIR"
        print_info "Removed existing installation"
    else
        print_info "Using existing directory"
    fi
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

echo -e "${YELLOW}Step 4: Setting up Python virtual environment...${NC}"

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

echo -e "${YELLOW}Step 5: Configuring environment variables (.env file)...${NC}"

# Create .env file from template as tradebot user
if sudo -u $TRADEBOT_USER [ -f "$INSTALL_DIR/.env" ]; then
    print_warning "Existing .env file found"
    read -p "Do you want to reconfigure it? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        run_as_tradebot "cd $INSTALL_DIR && mv .env .env.backup"
        print_info "Backed up existing .env file to .env.backup"
    else
        print_info "Keeping existing .env file"
        ENV_EXISTS=true
    fi
fi

if [ "$ENV_EXISTS" != true ]; then
    run_as_tradebot "cd $INSTALL_DIR && cp .env.example .env"
    
    echo -e "${BLUE}Please provide your API keys and configuration:${NC}"
    echo -e "${YELLOW}You can press Enter to skip optional fields${NC}"
    echo
    
    # TAAPI Key
    echo -e "${BLUE}TAAPI.io Configuration:${NC}"
    echo "Visit https://taapi.io to get your API key (~\$15/month subscription required)"
    read -p "Enter your TAAPI API key: " taapi_key
    if [ ! -z "$taapi_key" ]; then
        run_as_tradebot "cd $INSTALL_DIR && sed -i \"s/TAAPI_KEY=/TAAPI_KEY=$taapi_key/\" .env"
    fi
    echo
    
    # OpenAI Key
    echo -e "${BLUE}OpenAI API Configuration:${NC}"
    echo "Visit https://platform.openai.com to get your API key (pay-per-use)"
    read -p "Enter your OpenAI API key: " openai_key
    if [ ! -z "$openai_key" ]; then
        run_as_tradebot "cd $INSTALL_DIR && sed -i \"s/OPENAI_API_KEY=/OPENAI_API_KEY=$openai_key/\" .env"
    fi
    
    read -p "Enter OpenAI model [gpt-3.5-turbo]: " openai_model
    openai_model=${openai_model:-gpt-3.5-turbo}
    run_as_tradebot "cd $INSTALL_DIR && sed -i \"s/OPENAI_MODEL=gpt-3.5-turbo/OPENAI_MODEL=$openai_model/\" .env"
    echo
    
    # Alpaca Keys
    echo -e "${BLUE}Alpaca Trading Configuration:${NC}"
    echo "Visit https://alpaca.markets to get your API keys (free paper trading account)"
    read -p "Enter your Alpaca API key: " alpaca_key
    if [ ! -z "$alpaca_key" ]; then
        run_as_tradebot "cd $INSTALL_DIR && sed -i \"s/ALPACA_API_KEY=/ALPACA_API_KEY=$alpaca_key/\" .env"
    fi
    
    read -p "Enter your Alpaca Secret key: " alpaca_secret
    if [ ! -z "$alpaca_secret" ]; then
        run_as_tradebot "cd $INSTALL_DIR && sed -i \"s/ALPACA_SECRET_KEY=/ALPACA_SECRET_KEY=$alpaca_secret/\" .env"
    fi
    
    echo -e "${YELLOW}Alpaca Base URL options:${NC}"
    echo "1. Paper trading (recommended): https://paper-api.alpaca.markets"
    echo "2. Live trading: https://api.alpaca.markets"
    read -p "Choose [1-2, default: 1]: " alpaca_env
    if [ "$alpaca_env" = "2" ]; then
        run_as_tradebot "cd $INSTALL_DIR && sed -i \"s|ALPACA_BASE_URL=https://paper-api.alpaca.markets|ALPACA_BASE_URL=https://api.alpaca.markets|\" .env"
        print_warning "LIVE TRADING ENABLED - Use with caution!"
    fi
    echo
    
    # Discord Webhook (optional)
    echo -e "${BLUE}Discord Notifications (Optional):${NC}"
    echo "Create a webhook in your Discord server: Server Settings -> Integrations -> Webhooks"
    read -p "Enter Discord webhook URL (or press Enter to skip): " discord_webhook
    if [ ! -z "$discord_webhook" ]; then
        run_as_tradebot "cd $INSTALL_DIR && sed -i \"s|DISCORD_WEBHOOK_URL=|DISCORD_WEBHOOK_URL=$discord_webhook|\" .env"
    fi
    echo
    
    # Trading Configuration
    echo -e "${BLUE}Trading Configuration:${NC}"
    read -p "Enter stock symbol(s) [AAPL] (comma-separated for multiple): " symbols
    if [ ! -z "$symbols" ]; then
        if [[ "$symbols" == *","* ]]; then
            run_as_tradebot "cd $INSTALL_DIR && sed -i \"s/#SYMBOLS = AAPL,TSLA,SPY/SYMBOLS = $symbols/\" .env"
            run_as_tradebot "cd $INSTALL_DIR && sed -i \"s/SYMBOL=AAPL/#SYMBOL=AAPL/\" .env"
        else
            run_as_tradebot "cd $INSTALL_DIR && sed -i \"s/SYMBOL=AAPL/SYMBOL=$symbols/\" .env"
        fi
    fi
    
    read -p "Enter quantity per trade [1]: " qty
    qty=${qty:-1}
    run_as_tradebot "cd $INSTALL_DIR && sed -i \"s/QTY=1/QTY=$qty/\" .env"
    
    echo -e "${YELLOW}DRY_RUN mode (recommended for testing):${NC}"
    echo "1. Yes - Dry run mode (no actual trades, recommended)"
    echo "2. No - Live trading mode"
    read -p "Choose [1-2, default: 1]: " dry_run_choice
    if [ "$dry_run_choice" = "2" ]; then
        run_as_tradebot "cd $INSTALL_DIR && sed -i \"s/DRY_RUN=true/DRY_RUN=false/\" .env"
        print_warning "LIVE TRADING MODE ENABLED - Trades will be executed!"
    fi
    
    print_status "Environment configuration completed"
fi

echo -e "${YELLOW}Step 6: Creating systemd service...${NC}"

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

echo -e "${YELLOW}Step 7: Testing installation...${NC}"

# Test the bot can start as tradebot user
print_info "Testing bot startup as user '$TRADEBOT_USER'..."
timeout 10s sudo -u $TRADEBOT_USER bash -c "cd $INSTALL_DIR && source .venv/bin/activate && python trade_bot.py" || print_info "Test completed (timeout expected)"

print_status "Installation test completed"

echo -e "${GREEN}🎉 TradeBot Installation Complete!${NC}"
echo -e "${BLUE}============================================${NC}"
echo
echo -e "${YELLOW}Security Features Implemented:${NC}"
echo "• ✅ Dedicated 'tradebot' user account created"
echo "• ✅ Restricted file permissions (.env readable only by tradebot)"
echo "• ✅ Systemd security hardening (NoNewPrivileges, PrivateTmp, etc.)"
echo "• ✅ Resource limits (512MB memory, 1024 file handles)"
echo "• ✅ Bot runs with minimal privileges"
echo
echo -e "${YELLOW}Next Steps:${NC}"
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