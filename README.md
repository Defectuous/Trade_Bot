# RSI -> GPT -> Alpaca Trading Bot

## ⚠️ Important Notice - Subscription Services Required

**This trading bot requires active subscriptions to third-party services to function properly:**

- **🤖 OpenAI ChatGPT API**: Requires paid API access for trading decisions (not the free ChatGPT web interface)
- **📊 TAAPI.io**: Requires subscription for RSI technical indicator data  
- **📈 Alpaca Markets**: Free paper trading account available, live trading requires funding

**Without these subscriptions, the bot cannot make trading decisions or fetch market data.** Please ensure you have valid API keys and active subscriptions before running the bot.

---

## Overview

This small scaffold implements a minute-by-minute loop that:
- Fetches 6 technical indicators from TAAPI.io for configured symbols (RSI, MA, EMA, Three Black Crows, ADX, ADXR)
- Sends the indicator data to OpenAI (`gpt-3.5-turbo`) asking for a trading decision: BUY/SELL/NOTHING
- Uses the Alpaca Python SDK to place market orders (paper account recommended)
- **Supports fractional shares** for precise position sizing and better capital utilization
- Includes robust retry logic for API failures and server errors
- Provides comprehensive error handling and recovery mechanisms

## ✨ Key Features

- **📊 6 Technical Indicators**: Enhanced analysis with RSI, MA, EMA, Pattern Recognition, ADX, ADXR
- **🤖 AI-Powered Decisions**: GPT-3.5-turbo analyzes indicators and provides trading recommendations
- **💰 Fractional Share Support**: Trade partial shares (e.g., 0.5 shares) for better capital efficiency
- **💵 Dollar-Based Trading**: GPT can specify exact dollar amounts (e.g., "BUY $1000")
- **🔄 Smart Retry Logic**: Automatic recovery from API failures and server errors
- **🎛️ Granular Controls**: Enable/disable individual indicators via environment variables
- **📱 Discord Notifications**: Real-time trade alerts and daily summaries
- **🧪 Paper Trading**: Full testing support with Alpaca's paper trading environment

Files

- `trade_bot.py` - main script
- `requirements.txt` - Python dependencies
- `.env.example` - example environment variables

Quickstart

1. Create a Python 3.9+ virtual environment and install deps:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill your keys.

3. Run in dry-run first:

```powershell
$env:DRY_RUN = "true"; python .\trade_bot.py
```

## 💰 API Costs & Requirements

### Required Subscriptions:

**🤖 OpenAI API**
- **Cost**: Pay-per-use (typically $0.002 per 1K tokens for GPT-3.5-turbo)
- **Setup**: Create account at [platform.openai.com](https://platform.openai.com), add payment method, get API key
- **Usage**: ~1 API call per minute per symbol during trading hours
- **Estimated cost**: $1-5 per month for single symbol trading

**📊 TAAPI.io**
- **Cost**: Subscription plans start at ~$15/month for basic plan
- **Setup**: Create account at [taapi.io](https://taapi.io), subscribe to a plan, get API key
- **Usage**: RSI data fetched every minute during trading hours
- **Free tier**: Limited requests (may not be sufficient for continuous trading)

**📈 Alpaca Markets**
- **Paper Trading**: FREE - No cost for testing
- **Live Trading**: FREE account, but requires funding for actual trades
- **Setup**: Create account at [alpaca.markets](https://alpaca.markets), get API keys
- **Recommendation**: Start with paper trading to test the bot

**🔔 Discord Webhook (Optional)**
- **Cost**: FREE
- **Setup**: Create webhook in Discord server settings

### Total Monthly Cost Estimate:
- **Testing/Paper Trading**: ~$15-20/month (TAAPI + minimal OpenAI usage)  
- **Live Trading**: ~$15-25/month (depending on trading frequency)

---

## Notes

- The script uses US/Eastern hours (market open 9:30 to 16:00 ET).
- Default model is `gpt-3.5-turbo` but can be overridden with `OPENAI_MODEL`.
- Use `ALPACA_BASE_URL` to switch to paper/live endpoints. Default is paper.
- Always test in `DRY_RUN=true` and with Alpaca paper account before enabling live trading.
- The bot includes automatic retry logic for API failures (configurable via environment variables).

- You can monitor multiple symbols by setting a comma-separated `SYMBOLS` environment variable. This
	overrides `SYMBOL`. Example: `SYMBOLS=SPY,AAPL,TSLA`.

## 🔧 Troubleshooting

### Common Issues and Solutions

**🚨 Alpaca Server Errors (HTTP 5xx)**
```
ERROR Failed to fetch Alpaca account: 500 Server Error: Internal Server Error
```
**Solution**: The bot now includes automatic retry logic. Configure retry behavior in `.env`:
```bash
ALPACA_RETRY_ATTEMPTS=3    # Number of retry attempts (default: 3)
ALPACA_RETRY_DELAY=2       # Initial delay in seconds (default: 2)  
ALPACA_RETRY_BACKOFF=2     # Exponential backoff multiplier (default: 2)
```

**� Authentication Issues**
```
alpaca_trade_api.rest.APIError: unauthorized.
```
**Solution**: This indicates invalid or misconfigured Alpaca API credentials:

1. **Verify API Keys**: Check your `.env` file has correct credentials:
   ```bash
   ALPACA_API_KEY=PK...     # Should start with 'PK' for paper trading
   ALPACA_SECRET_KEY=...    # Long secret key
   ALPACA_BASE_URL=https://paper-api.alpaca.markets  # Paper trading endpoint
   ```

2. **Check Paper vs Live Trading**: Ensure you're using the correct endpoint:
   - **Paper Trading**: `https://paper-api.alpaca.markets` (recommended)
   - **Live Trading**: `https://api.alpaca.markets` (requires funded account)

3. **Test API Connection**: Run the diagnostic script:
   ```bash
   python test_alpaca_auth.py
   ```

4. **Generate New Keys**: If keys are invalid:
   - Log into [alpaca.markets](https://alpaca.markets)
   - Go to 'Paper Trading' section
   - Generate new API keys
   - Update your `.env` file with exact values

5. **Restart Service**: After updating credentials:
   ```bash
   sudo systemctl restart trade_bot.service
   sudo journalctl -u trade_bot.service -f
   ```

**�📊 TAAPI Rate Limits**
```
ERROR Failed to fetch indicators: 429 Too Many Requests
```
**Solution**: Upgrade your TAAPI.io plan or reduce trading frequency by monitoring fewer symbols.

**🤖 OpenAI API Errors**
```
ERROR GPT error: Rate limit exceeded
```
**Solution**: Check your OpenAI API usage and billing. Consider upgrading your plan or reducing request frequency.

**🔑 Authentication Issues**
```
ERROR Alpaca credentials not set
```
**Solution**: Verify your `.env` file contains valid API keys:
```bash
ALPACA_API_KEY=your_alpaca_key
ALPACA_SECRET_KEY=your_alpaca_secret  
ALPACA_BASE_URL=https://paper-api.alpaca.markets  # For paper trading
```

**🕒 Market Hours Issues**
```
INFO Market closed: outside trading hours
```
**Solution**: This is normal behavior. The bot only trades during market hours (9:30 AM - 4:00 PM ET, Mon-Fri).

**🔧 Alpaca SDK Version Issues**
```
AttributeError: 'REST' object has no attribute 'get_last_trade'
AttributeError: 'REST' object has no attribute 'get_barset'
```
**Solution**: The bot has been updated to use modern Alpaca SDK methods. If you encounter this error:
1. Update your Alpaca SDK: `pip install --upgrade alpaca-trade-api`
2. The bot automatically tries multiple price fetching methods:
   - `get_latest_quote()` - Uses bid/ask mid-price
   - `get_bars()` - Uses latest bar close price  
   - `get_snapshot()` - Uses snapshot data
3. Check logs for which method succeeded: `journalctl -u trade_bot.service -f`

### Testing API Connections

Run the test script to verify all APIs are working:
```bash
python test_retry_logic.py
```

This will test Alpaca connectivity and show retry behavior in action.

For detailed price fetching testing with modern SDK methods:
```bash
python test_price_methods.py
```

This will specifically test the updated price fetching methods and show which fallback methods are used.

## 🚀 Installation Guide

### Automated Installation (Recommended)

Choose the appropriate installation script for your operating system:

#### 🐧 **Linux/Raspberry Pi Installation**

**Features:**
- ✅ Creates dedicated `tradebot` user account for security
- ✅ Sets up systemd service with security hardening
- ✅ Configures proper file permissions and access controls
- ✅ Installs dependencies and virtual environment
- ✅ Interactive API key configuration

**Requirements:**
- Linux/Raspberry Pi OS/Debian/Ubuntu
- Internet connection
- User with sudo privileges

**Installation:**
```bash
# Download and run the installation script
curl -sSL https://raw.githubusercontent.com/Defectuous/Trade_Bot/main/install_tradebot.sh | bash

# Or download and inspect first (recommended)
wget https://raw.githubusercontent.com/Defectuous/Trade_Bot/main/install_tradebot.sh
chmod +x install_tradebot.sh
./install_tradebot.sh
```

**⚠️ Important:** Do NOT run with `sudo`. The script will prompt for sudo when needed.

#### 🪟 **Windows Installation**

**Features:**
- ✅ Creates dedicated `tradebot` user account for security
- ✅ Sets up Windows Scheduled Task for automated execution
- ✅ Configures proper file permissions and access controls
- ✅ Installs Python dependencies in virtual environment
- ✅ Interactive API key configuration with secure storage

**Requirements:**
- Windows 10/11
- Python 3.8+ installed and added to PATH
- Git for Windows
- Administrator privileges

**Installation:**
1. **Open PowerShell as Administrator** (Right-click PowerShell → "Run as Administrator")

2. **Set execution policy** (if needed):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

3. **Download and run the installation script**:
```powershell
# Download the script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Defectuous/Trade_Bot/main/install_tradebot.ps1" -OutFile "install_tradebot.ps1"

# Run the installation
.\install_tradebot.ps1
```

**Post-Installation Management:**

**Linux (systemd service):**
```bash
# Start/stop the service
sudo systemctl start trade_bot.service
sudo systemctl stop trade_bot.service

# Enable/disable automatic startup
sudo systemctl enable trade_bot.service
sudo systemctl disable trade_bot.service

# View logs
sudo journalctl -u trade_bot.service -f

# Edit configuration as tradebot user
sudo -u tradebot nano /home/tradebot/Trade_Bot/.env
```

**Windows (scheduled task):**
```powershell
# Start/stop the scheduled task
Start-ScheduledTask -TaskName "TradeBot"
Stop-ScheduledTask -TaskName "TradeBot"

# View task status
Get-ScheduledTask -TaskName "TradeBot"
Get-ScheduledTaskInfo -TaskName "TradeBot"

# Edit configuration
notepad C:\Trade_Bot\.env
```

### 🔒 Security Features

Both installation scripts implement enterprise-grade security:

- **Dedicated User Account**: Bot runs under `tradebot` user, not your main account
- **File Permissions**: `.env` file readable only by `tradebot` user
- **Service Hardening**: Restricted system access and resource limits
- **API Key Protection**: Secure storage with minimal file permissions

### Manual Installation

If you prefer to install manually or need custom configuration:

#### Linux/Raspberry Pi Manual Setup

1. **Install system packages:**
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
```

2. **Clone repository:**
```bash
git clone https://github.com/Defectuous/Trade_Bot.git
cd Trade_Bot
```

3. **Create virtual environment:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

4. **Install dependencies:**
```bash
pip install -r requirements.txt
```

5. **Configure environment:**
```bash
cp .env.example .env
nano .env  # Add your API keys
```

#### Windows Manual Setup

1. **Install prerequisites:**
   - Python 3.8+ from [python.org](https://python.org)
   - Git from [git-scm.com](https://git-scm.com)

2. **Clone repository:**
```powershell
git clone https://github.com/Defectuous/Trade_Bot.git
cd Trade_Bot
```

3. **Create virtual environment:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

4. **Install dependencies:**
```powershell
pip install -r requirements.txt
```

5. **Configure environment:**
```powershell
Copy-Item .env.example .env
notepad .env  # Add your API keys
```

### 📝 Environment Configuration

After installation (manual or automated), configure your API keys and trading settings in the `.env` file:

**Required API Keys:**
```bash
# TAAPI.io API Configuration
TAAPI_KEY=your_taapi_api_key_here

# OpenAI API Configuration  
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# Alpaca Trading API Configuration
ALPACA_API_KEY=your_alpaca_api_key_here
ALPACA_SECRET_KEY=your_alpaca_secret_key_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets  # Use paper trading for testing
```

**Trading Configuration:**
```bash
# Trading Settings
SYMBOL=AAPL                    # Single symbol trading
# OR use multiple symbols:
# SYMBOLS=AAPL,TSLA,SPY       # Multiple symbol trading (overrides SYMBOL)

QTY=1                          # Supports fractional shares: 1, 0.5, 1.25, etc.
DRY_RUN=true                   # Set to false for live trading (test first!)
LOG_LEVEL=INFO

# Technical Indicator Controls (Optional)
ENABLE_RSI=true                # Relative Strength Index
ENABLE_MA=true                 # Moving Average
ENABLE_EMA=true                # Exponential Moving Average  
ENABLE_PATTERN=true            # Three Black Crows pattern
ENABLE_ADX=true                # Average Directional Index
ENABLE_ADXR=true               # Average Directional Index Rating

# Technical Indicator Periods (Optional)
MA_PERIOD=20                   # Moving Average period
EMA_PERIOD=12                  # Exponential Moving Average period
ADX_PERIOD=14                  # ADX calculation period
ADXR_PERIOD=14                 # ADXR calculation period

# Discord Notifications (Optional)
DISCORD_WEBHOOK_URL=your_discord_webhook_url_here
```

**⚠️ Security Notes:**
- Keep your `.env` file secure and never commit it to version control
- Start with `DRY_RUN=true` and paper trading to test the bot
- Use paper trading (`https://paper-api.alpaca.markets`) before live trading

### 🧪 Testing Your Installation

**Test with dry run:**
```bash
# Linux
sudo -u tradebot bash -c 'cd /home/tradebot/Trade_Bot && source .venv/bin/activate && python trade_bot.py'

# Windows  
cd C:\Trade_Bot
.\.venv\Scripts\Activate.ps1
python trade_bot.py
```

**Run the diagnostic tests:**
```bash
# Test API connections
python tests/test_alpaca_auth.py
python tests/validate_alpaca_functions.py

# Test fractional shares support
python tests/test_fractional_shares.py
```

### 🔧 Advanced Configuration

**Retry Logic Configuration:**
```bash
ALPACA_RETRY_ATTEMPTS=3        # Number of retry attempts
ALPACA_RETRY_DELAY=2           # Initial delay in seconds
ALPACA_RETRY_BACKOFF=2         # Exponential backoff multiplier
```

**Logging Configuration:**
```bash
LOG_LEVEL=INFO                 # DEBUG, INFO, WARNING, ERROR
LOG_FILE=log/TradeBot.{date}.{time}.log  # Log file pattern
```

## 🏃‍♂️ Quick Start Guide

1. **Choose your installation method** (Automated scripts recommended)
2. **Configure your API keys** in the `.env` file
3. **Test with paper trading**: Ensure `DRY_RUN=true` and `ALPACA_BASE_URL=https://paper-api.alpaca.markets`
4. **Run a test**: Execute the bot manually to verify everything works
5. **Start the service**: Use systemd (Linux) or scheduled task (Windows)
6. **Monitor**: Check logs and trading activity
7. **Go live**: Only after thorough testing, switch to live trading

## 📚 Additional Documentation

- **[Security Setup Guide](guides/SECURITY_SETUP.md)** - Detailed security features and best practices
- **[Fractional Shares Guide](guides/FRACTIONAL_SHARES.md)** - How to use fractional share trading
- **[Small Account Guide](guides/SMALL_ACCOUNT_GUIDE.md)** - Optimizations for smaller trading accounts

---

## 🔧 Legacy Manual Installation (Advanced Users)

For advanced users who prefer complete manual control:

### Legacy Linux Setup

1. **Install system packages:**
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
```

2. **Clone and setup:**
```bash
git clone https://github.com/Defectuous/Trade_Bot.git
cd Trade_Bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
nano .env  # Add your API keys
```

4. **Test the bot:**
```bash
source .venv/bin/activate
python3 ./trade_bot.py
```

5. **Optional: Run in background with tmux:**
```bash
sudo apt install -y tmux
tmux new -s tradebot
# Inside tmux session:
source .venv/bin/activate
python3 ./trade_bot.py
# Detach with: Ctrl-B then D
```

6. **Optional: Create systemd service:**
Create `/etc/systemd/system/trade_bot.service`:
```ini
[Unit]
Description=AI Trading Bot with Enhanced Technical Analysis
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Trade_Bot
EnvironmentFile=/home/pi/Trade_Bot/.env
ExecStart=/home/pi/Trade_Bot/.venv/bin/python /home/pi/Trade_Bot/trade_bot.py
Restart=on-failure
RestartSec=30s

[Install]
WantedBy=multi-user.target
```

Then enable and manage:
```bash
sudo systemctl daemon-reload
sudo systemctl enable trade_bot.service
sudo systemctl start trade_bot.service
sudo journalctl -u trade_bot.service -f
```

## ⚠️ Important Notes

- **Security First**: Use the automated installation scripts for better security
- **Test Thoroughly**: Always test with `DRY_RUN=true` and paper trading first
- **API Limits**: Monitor TAAPI.io rate limits when using multiple symbols
- **Keep Secrets Safe**: Secure your `.env` file and never commit it to version control
- **Monitor Regularly**: Check logs and trading performance frequently

## 📞 Support

For questions, issues, or contributions:
- Check the GitHub repository for updates
- Review the comprehensive documentation in the `/guides` folder
- Test all changes in paper trading mode first
