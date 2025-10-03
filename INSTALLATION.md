# TradeBot Installation Guide

## Quick Two-Step Installation

### Step 1: Create TradeBot User
First, create the dedicated user account for security:

```bash
curl -sSL https://raw.githubusercontent.com/Defectuous/Trade_Bot/main/create_tradebot_user.sh | bash
```

This will:
- Create a `tradebot` user with interactive password setup
- Add the user to the `sudo` group for necessary privileges
- Verify the user setup is complete

### Step 2: Install TradeBot
After the user is created, install the trading bot:

```bash
curl -sSL https://raw.githubusercontent.com/Defectuous/Trade_Bot/main/install_tradebot.sh | bash
```

This will:
- Update the system packages
- Clone the TradeBot repository
- Set up Python virtual environment
- Install dependencies
- Create systemd service
- Set up default configuration

## Post-Installation Configuration

### 1. Configure API Keys
Edit the configuration file:
```bash
sudo -u tradebot nano /home/tradebot/Trade_Bot/.env
```

Add your API keys:
```bash
# Required API Keys
TAAPI_KEY=your_taapi_key_here
OPENAI_API_KEY=your_openai_key_here
ALPACA_API_KEY=your_alpaca_key_here
ALPACA_SECRET_KEY=your_alpaca_secret_here
```

### 2. Start the Trading Bot
```bash
# Enable auto-start on boot
sudo systemctl enable trade_bot.service

# Start the service
sudo systemctl start trade_bot.service

# Check status
sudo systemctl status trade_bot.service

# View logs
sudo journalctl -u trade_bot.service -f
```

## API Key Sources

- **TAAPI.io**: Get technical indicators API key (~$15/month) - https://taapi.io
- **OpenAI**: Get GPT API key (pay-per-use) - https://platform.openai.com
- **Alpaca**: Get trading API keys (free paper trading) - https://alpaca.markets

## Security Features

- ✅ Dedicated user account (`tradebot`)
- ✅ Restricted file permissions
- ✅ Systemd security hardening
- ✅ Resource limits (512MB memory)
- ✅ DRY_RUN mode by default (safe for testing)

## Manual Installation (Alternative)

If you prefer to create the user manually:

```bash
# Create user
sudo adduser tradebot
sudo usermod -a -G sudo tradebot

# Then run the installation script
curl -sSL https://raw.githubusercontent.com/Defectuous/Trade_Bot/main/install_tradebot.sh | bash
```

## Troubleshooting

### User Creation Issues
If the user creation script fails:
```bash
# Check if user exists
id tradebot

# Check user groups
groups tradebot

# Manually add sudo privileges if needed
sudo usermod -a -G sudo tradebot
```

### Installation Issues
If the main installation fails:
```bash
# Check if tradebot user exists
id tradebot

# Manually clone repository if needed
sudo -u tradebot git clone https://github.com/Defectuous/Trade_Bot.git /home/tradebot/Trade_Bot

# Check Python environment
sudo -u tradebot python3 --version
```

### Service Issues
If the trading bot service won't start:
```bash
# Check service status
sudo systemctl status trade_bot.service

# View detailed logs
sudo journalctl -u trade_bot.service --no-pager

# Test manual startup
sudo -u tradebot bash -c 'cd /home/tradebot/Trade_Bot && source .venv/bin/activate && python trade_bot.py'
```