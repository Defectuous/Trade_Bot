# TradeBot Security Setup Guide

## Overview
The TradeBot installation scripts now include enhanced security features by creating a dedicated user account specifically for running the trading bot. This follows security best practices for financial applications.

## Security Features

### 🔒 **Dedicated User Account**
- **Linux/Raspberry Pi**: Creates `tradebot` user account
- **Windows**: Creates `tradebot` user account with restricted privileges
- Bot runs under this dedicated account, not your main user account
- Limits potential security exposure if the bot is compromised

### 🔒 **File Permission Security**
- `.env` file is readable only by the `tradebot` user (600 permissions on Linux)
- Installation directory has proper ownership and access controls
- Log files are written to restricted directories

### 🔒 **Service Security Hardening**
#### Linux (systemd service):
- `NoNewPrivileges=yes` - Prevents privilege escalation
- `PrivateTmp=yes` - Isolated temporary directory
- `ProtectSystem=strict` - Read-only system directories
- `ProtectHome=yes` - Home directories are inaccessible
- `ReadWritePaths` - Only specific directories are writable
- Memory and file handle limits

#### Windows (Scheduled Task):
- Runs under dedicated user account
- Restricted file system access
- Scheduled execution during market hours only

## Installation Methods

### 🐧 **Linux/Raspberry Pi Installation**
```bash
# Download and run the installation script
curl -sSL https://raw.githubusercontent.com/Defectuous/TradeBot/main/install_tradebot.sh | bash

# Or download and inspect first (recommended)
wget https://raw.githubusercontent.com/Defectuous/TradeBot/main/install_tradebot.sh
chmod +x install_tradebot.sh
./install_tradebot.sh
```

### 🪟 **Windows Installation**
```powershell
# Set execution policy (run as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Download and run the installation script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Defectuous/TradeBot/main/install_tradebot.ps1" -OutFile "install_tradebot.ps1"
.\install_tradebot.ps1
```

## Security Benefits

### **Principle of Least Privilege**
- Bot runs with minimal necessary permissions
- Cannot access other user accounts or system files
- Limited resource usage (memory, file handles)

### **Isolation**
- Bot is isolated from your main user environment
- API keys are secured with restrictive file permissions
- Log files are contained within the bot's directory

### **Monitoring & Control**
- Service/task runs under system management
- Easy to start, stop, and monitor
- Logs are centralized and accessible to administrators

## Post-Installation Security Checklist

### ✅ **Verify User Account**
```bash
# Linux: Check tradebot user exists
id tradebot

# Windows: Check tradebot user exists
Get-LocalUser -Name tradebot
```

### ✅ **Verify File Permissions**
```bash
# Linux: Check .env file permissions (should be 600)
ls -la /home/tradebot/TradeBot/.env

# Windows: Check .env file ACL
Get-Acl C:\TradeBot\.env | Format-List
```

### ✅ **Test Service Security**
```bash
# Linux: Check service status and security settings
sudo systemctl status trade_bot.service
sudo systemctl show trade_bot.service | grep -E "(User|NoNewPrivileges|PrivateTmp)"

# Windows: Check scheduled task
Get-ScheduledTask -TaskName "TradeBot"
```

## Managing the Secure Installation

### **Starting/Stopping the Bot**
```bash
# Linux
sudo systemctl start trade_bot.service
sudo systemctl stop trade_bot.service

# Windows
Start-ScheduledTask -TaskName "TradeBot"
Stop-ScheduledTask -TaskName "TradeBot"
```

### **Viewing Logs**
```bash
# Linux
sudo journalctl -u trade_bot.service -f

# Windows
Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-TaskScheduler/Operational'}
```

### **Updating Configuration**
```bash
# Linux: Edit as tradebot user
sudo -u tradebot nano /home/tradebot/TradeBot/.env

# Windows: Edit with proper permissions
notepad C:\TradeBot\.env
```

### **Manual Testing**
```bash
# Linux: Test as tradebot user
sudo -u tradebot bash -c 'cd /home/tradebot/TradeBot && source .venv/bin/activate && python trade_bot.py'

# Windows: Test with current permissions
cd C:\TradeBot
.\.venv\Scripts\Activate.ps1
python trade_bot.py
```

## Security Considerations

### **API Key Protection**
- `.env` file is only readable by the `tradebot` user
- Never commit `.env` files to version control
- Rotate API keys regularly
- Use paper trading accounts for testing

### **Network Security**
- Bot only makes outbound HTTPS connections to:
  - TAAPI.io (technical indicators)
  - OpenAI API (trading decisions)
  - Alpaca API (trade execution)
  - Discord webhooks (notifications)
- No inbound network connections required

### **System Monitoring**
- Monitor system logs for unusual activity
- Set up alerts for service failures
- Regularly review trading logs and performance
- Monitor resource usage (CPU, memory, network)

### **Backup Strategy**
- Backup configuration files regularly
- Keep secure copies of API keys
- Document your trading strategy and settings
- Test restore procedures

## Troubleshooting Security Issues

### **Permission Denied Errors**
```bash
# Linux: Fix ownership and permissions
sudo chown -R tradebot:tradebot /home/tradebot/TradeBot
sudo chmod 600 /home/tradebot/TradeBot/.env

# Windows: Reset permissions
icacls C:\TradeBot /grant tradebot:F /T
```

### **Service Won't Start**
```bash
# Linux: Check service logs
sudo journalctl -u trade_bot.service --no-pager

# Windows: Check task history
Get-ScheduledTaskInfo -TaskName "TradeBot"
```

### **API Authentication Failures**
- Verify API keys are correctly set in `.env`
- Check API key permissions and limits
- Ensure network connectivity to API endpoints
- Test with minimal permissions first

## Migration from Non-Secure Installation

If you have an existing TradeBot installation running under your main user account:

### **Backup Current Installation**
```bash
# Create backup
cp -r /path/to/current/Trade_Bot /path/to/backup/Trade_Bot_backup
```

### **Run New Secure Installation**
```bash
# This will create the new secure installation
./install_tradebot.sh
```

### **Migrate Configuration**
```bash
# Copy your .env configuration to new installation
sudo cp /path/to/backup/Trade_Bot_backup/.env /home/tradebot/TradeBot/.env
sudo chown tradebot:tradebot /home/tradebot/TradeBot/.env
sudo chmod 600 /home/tradebot/TradeBot/.env
```

### **Stop Old Installation**
```bash
# Stop any old services or processes
sudo systemctl stop old_trade_bot.service  # if applicable
pkill -f trade_bot.py  # stop any running instances
```

## Support and Updates

For security-related questions or to report security issues:
- Check the GitHub repository for updates
- Review the security documentation
- Test all changes in paper trading mode first
- Keep the bot and its dependencies updated

Remember: **Security is an ongoing process, not a one-time setup!**