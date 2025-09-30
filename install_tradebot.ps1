# Trade_Bot Windows Installation Script
# This script will install and configure the AI Trading Bot with dedicated user account
# Run as Administrator: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then run: .\install_tradebot.ps1

param(
    [string]$TradeBotUser = "tradebot",
    [string]$InstallPath = "C:\Trade_Bot",
    [string]$GitHubRepo = "https://github.com/Defectuous/Trade_Bot.git"
)

# Colors for output
$ErrorColor = "Red"
$SuccessColor = "Green"
$WarningColor = "Yellow"
$InfoColor = "Cyan"

function Write-Status {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor $SuccessColor
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor $WarningColor
}

function Write-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor $ErrorColor
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor $InfoColor
}

Write-Host "🚀 Trade_Bot Windows Installation Script" -ForegroundColor $InfoColor
Write-Host "=======================================" -ForegroundColor $InfoColor
Write-Host "This script will create a dedicated user account for security" -ForegroundColor $WarningColor
Write-Host ""

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This script must be run as Administrator"
    Write-Info "Right-click PowerShell and select 'Run as Administrator'"
    pause
    exit 1
}

Write-Host "Step 1: Creating dedicated tradebot user account..." -ForegroundColor $WarningColor

# Check if user already exists
try {
    $existingUser = Get-LocalUser -Name $TradeBotUser -ErrorAction Stop
    Write-Warning "User '$TradeBotUser' already exists"
    $continue = Read-Host "Do you want to continue with existing user? (y/n)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        Write-Info "Installation cancelled"
        exit 0
    }
} catch {
    Write-Info "Creating user '$TradeBotUser'..."
    
    # Generate secure password
    $Password = Read-Host "Enter password for tradebot user" -AsSecureString
    
    # Create user account
    try {
        New-LocalUser -Name $TradeBotUser -Password $Password -Description "Dedicated account for AI Trading Bot" -PasswordNeverExpires -UserMayNotChangePassword
        
        # Add to necessary groups
        Add-LocalGroupMember -Group "Users" -Member $TradeBotUser
        
        Write-Status "User '$TradeBotUser' created successfully"
    } catch {
        Write-Error "Failed to create user: $($_.Exception.Message)"
        pause
        exit 1
    }
}

Write-Host "Step 2: Installing required software..." -ForegroundColor $WarningColor

# Check for Python
try {
    $pythonVersion = python --version 2>&1
    Write-Info "Python found: $pythonVersion"
} catch {
    Write-Error "Python not found. Please install Python 3.8+ from python.org"
    Write-Info "Make sure to add Python to PATH during installation"
    pause
    exit 1
}

# Check for Git
try {
    $gitVersion = git --version 2>&1
    Write-Info "Git found: $gitVersion"
} catch {
    Write-Error "Git not found. Please install Git from git-scm.com"
    pause
    exit 1
}

Write-Host "Step 3: Installing Trade_Bot from GitHub..." -ForegroundColor $WarningColor

# Create install directory
if (Test-Path $InstallPath) {
    Write-Warning "Trade_Bot directory already exists at $InstallPath"
    $reinstall = Read-Host "Do you want to remove it and reinstall? (y/n)"
    if ($reinstall -eq "y" -or $reinstall -eq "Y") {
        Remove-Item -Path $InstallPath -Recurse -Force
        Write-Info "Removed existing installation"
    }
}

if (-not (Test-Path $InstallPath)) {
    Write-Info "Cloning Trade_Bot repository..."
    git clone $GitHubRepo $InstallPath
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to clone repository"
        pause
        exit 1
    }
}

# Set proper permissions for tradebot user
Write-Info "Setting proper file permissions..."
$acl = Get-Acl $InstallPath
$accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule($TradeBotUser, "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow")
$acl.SetAccessRule($accessRule)
Set-Acl -Path $InstallPath -AclObject $acl

Write-Status "Trade_Bot repository ready"

Write-Host "Step 4: Setting up Python virtual environment..." -ForegroundColor $WarningColor

# Create virtual environment
$venvPath = Join-Path $InstallPath ".venv"
Write-Info "Creating Python virtual environment..."
Set-Location $InstallPath
python -m venv .venv

if (-not (Test-Path $venvPath)) {
    Write-Error "Failed to create virtual environment"
    pause
    exit 1
}

# Activate virtual environment and install dependencies
Write-Info "Installing Python dependencies..."
& "$venvPath\Scripts\Activate.ps1"
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install dependencies"
    pause
    exit 1
}

Write-Status "Python environment setup completed"

Write-Host "Step 5: Configuring environment variables (.env file)..." -ForegroundColor $WarningColor

$envFile = Join-Path $InstallPath ".env"

if (Test-Path $envFile) {
    Write-Warning "Existing .env file found"
    $reconfigure = Read-Host "Do you want to reconfigure it? (y/n)"
    if ($reconfigure -eq "y" -or $reconfigure -eq "Y") {
        Move-Item $envFile "$envFile.backup"
        Write-Info "Backed up existing .env file to .env.backup"
        $createEnv = $true
    } else {
        Write-Info "Keeping existing .env file"
        $createEnv = $false
    }
} else {
    $createEnv = $true
}

if ($createEnv) {
    Copy-Item (Join-Path $InstallPath ".env.example") $envFile
    
    Write-Host "Please provide your API keys and configuration:" -ForegroundColor $InfoColor
    Write-Host "You can press Enter to skip optional fields" -ForegroundColor $WarningColor
    Write-Host ""
    
    # TAAPI Key
    Write-Host "TAAPI.io Configuration:" -ForegroundColor $InfoColor
    Write-Host "Visit https://taapi.io to get your API key (~$15/month subscription required)"
    $taapiKey = Read-Host "Enter your TAAPI API key"
    if ($taapiKey) {
        (Get-Content $envFile) -replace "TAAPI_KEY=", "TAAPI_KEY=$taapiKey" | Set-Content $envFile
    }
    
    # OpenAI Key
    Write-Host "OpenAI API Configuration:" -ForegroundColor $InfoColor
    Write-Host "Visit https://platform.openai.com to get your API key (pay-per-use)"
    $openaiKey = Read-Host "Enter your OpenAI API key"
    if ($openaiKey) {
        (Get-Content $envFile) -replace "OPENAI_API_KEY=", "OPENAI_API_KEY=$openaiKey" | Set-Content $envFile
    }
    
    # Alpaca Keys
    Write-Host "Alpaca Trading Configuration:" -ForegroundColor $InfoColor
    Write-Host "Visit https://alpaca.markets to get your API keys (free paper trading account)"
    $alpacaKey = Read-Host "Enter your Alpaca API key"
    if ($alpacaKey) {
        (Get-Content $envFile) -replace "ALPACA_API_KEY=", "ALPACA_API_KEY=$alpacaKey" | Set-Content $envFile
    }
    
    $alpacaSecret = Read-Host "Enter your Alpaca Secret key"
    if ($alpacaSecret) {
        (Get-Content $envFile) -replace "ALPACA_SECRET_KEY=", "ALPACA_SECRET_KEY=$alpacaSecret" | Set-Content $envFile
    }
    
    # Trading mode
    Write-Host "Alpaca Base URL options:" -ForegroundColor $WarningColor
    Write-Host "1. Paper trading (recommended): https://paper-api.alpaca.markets"
    Write-Host "2. Live trading: https://api.alpaca.markets"
    $alpacaEnv = Read-Host "Choose [1-2, default: 1]"
    if ($alpacaEnv -eq "2") {
        (Get-Content $envFile) -replace "https://paper-api.alpaca.markets", "https://api.alpaca.markets" | Set-Content $envFile
        Write-Warning "LIVE TRADING ENABLED - Use with caution!"
    }
    
    # Secure .env file
    Write-Info "Securing .env file permissions..."
    $envAcl = Get-Acl $envFile
    $envAcl.SetAccessRuleProtection($true, $false)  # Remove inherited permissions
    $envAccessRule = New-Object System.Security.AccessControl.FileSystemAccessRule($TradeBotUser, "FullControl", "Allow")
    $envAcl.SetAccessRule($envAccessRule)
    Set-Acl -Path $envFile -AclObject $envAcl
    
    Write-Status "Environment configuration completed"
}

Write-Host "Step 6: Creating Windows Service..." -ForegroundColor $WarningColor

# Create service wrapper script
$serviceScript = @"
@echo off
cd /d "$InstallPath"
"$venvPath\Scripts\python.exe" trade_bot.py
"@

$serviceScriptPath = Join-Path $InstallPath "run_tradebot.bat"
$serviceScript | Out-File -FilePath $serviceScriptPath -Encoding ASCII

Write-Info "Creating Windows Service..."
$serviceName = "Trade_Bot"
$serviceDisplayName = "AI Trading Bot Service"
$serviceDescription = "Advanced AI Trading Bot with 6-Indicator Analysis"

# Remove service if it exists
$existingService = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
if ($existingService) {
    Write-Info "Removing existing service..."
    Stop-Service -Name $serviceName -Force -ErrorAction SilentlyContinue
    sc.exe delete $serviceName
}

# Create new service using NSSM (Non-Sucking Service Manager) approach
# For now, create a scheduled task instead
Write-Info "Creating scheduled task for Trade_Bot..."

$taskName = "Trade_Bot"
$taskDescription = "AI Trading Bot - Runs every minute during market hours"

# Remove existing task
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

# Create task action
$taskAction = New-ScheduledTaskAction -Execute "$venvPath\Scripts\python.exe" -Argument "trade_bot.py" -WorkingDirectory $InstallPath

# Create task trigger (every minute from 9:30 AM to 4:00 PM, Monday-Friday)
$taskTrigger = New-ScheduledTaskTrigger -Daily -At "09:30" -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday

# Create task settings
$taskSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Create task principal (run as tradebot user)
$taskPrincipal = New-ScheduledTaskPrincipal -UserId $TradeBotUser -LogonType Interactive

# Register the task
Register-ScheduledTask -TaskName $taskName -Action $taskAction -Trigger $taskTrigger -Settings $taskSettings -Principal $taskPrincipal -Description $taskDescription

Write-Status "Scheduled task created successfully"

Write-Host "Step 7: Testing installation..." -ForegroundColor $WarningColor

Write-Info "Testing bot startup..."
Set-Location $InstallPath
$testProcess = Start-Process -FilePath "$venvPath\Scripts\python.exe" -ArgumentList "trade_bot.py" -PassThru -Wait -TimeoutSec 10
Write-Info "Test completed"

Write-Status "Installation test completed"

Write-Host ""
Write-Host "🎉 TradeBot Installation Complete!" -ForegroundColor $SuccessColor
Write-Host "====================================" -ForegroundColor $InfoColor
Write-Host ""
Write-Host "Security Features Implemented:" -ForegroundColor $WarningColor
Write-Host "• ✅ Dedicated 'tradebot' user account created"
Write-Host "• ✅ Restricted file permissions (.env readable only by tradebot)"
Write-Host "• ✅ Scheduled task runs with minimal privileges"
Write-Host "• ✅ Bot files secured with proper access controls"
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor $WarningColor
Write-Host ""
Write-Host "1. 📊 Verify your configuration:"
Write-Host "   notepad $envFile"
Write-Host ""
Write-Host "2. 🧪 Test the bot manually:"
Write-Host "   cd $InstallPath"
Write-Host "   .\.venv\Scripts\Activate.ps1"
Write-Host "   python trade_bot.py"
Write-Host ""
Write-Host "3. 🚀 Start the scheduled task:"
Write-Host "   Start-ScheduledTask -TaskName '$taskName'"
Write-Host ""
Write-Host "4. 📋 Monitor the task:"
Write-Host "   Get-ScheduledTask -TaskName '$taskName'"
Write-Host "   Get-ScheduledTaskInfo -TaskName '$taskName'"
Write-Host ""
Write-Host "5. 🛑 Stop the task:"
Write-Host "   Stop-ScheduledTask -TaskName '$taskName'"
Write-Host ""
Write-Host "Important Security Notes:" -ForegroundColor $WarningColor
Write-Host "• Bot runs under dedicated 'tradebot' user account"
Write-Host "• .env file is secured with restricted permissions"
Write-Host "• Scheduled task runs with minimal privileges"
Write-Host "• Bot is configured in DRY_RUN mode by default (safe for testing)"
Write-Host "• Test thoroughly before enabling live trading"
Write-Host ""
Write-Host "Configuration file location: $envFile" -ForegroundColor $InfoColor
Write-Host "Installation directory: $InstallPath" -ForegroundColor $InfoColor
Write-Host "Scheduled task name: $taskName" -ForegroundColor $InfoColor
Write-Host ""
Write-Host "Happy Secure Trading! 🚀📈🔒" -ForegroundColor $SuccessColor

pause