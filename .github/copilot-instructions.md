# GitHub Copilot Instructions for Enhanced Trading Bot

## Project Overview
This is an advanced Python trading bot that integrates **6 technical indicators** with AI-powered decision making for automated stock trading. The system combines TAAPI.io technical analysis, OpenAI GPT-3.5-turbo for trading decisions, and Alpaca API for trade execution.

## Architecture & Components

### Core Modules
- **`trade_bot.py`** - Main orchestrator with scheduling, market hours validation, and trading loop
- **`modules/taapi.py`** - Enhanced technical indicators client (6 indicators vs original RSI-only)
- **`modules/gpt_client.py`** - OpenAI GPT client with sophisticated technical analysis prompts
- **`modules/alpaca_client.py`** - Alpaca API wrapper for trade execution and portfolio management
- **`modules/market_schedule.py`** - Market hours validation and trading session management
- **`modules/discord_webhook.py`** - Trade notifications and daily summaries

### Enhanced Technical Analysis System
The bot uses **6 technical indicators** for comprehensive market analysis:

1. **RSI (Relative Strength Index)** - Momentum oscillator (overbought/oversold)
2. **MA (Moving Average)** - Trend direction and support/resistance
3. **EMA (Exponential Moving Average)** - Recent price-weighted trend analysis
4. **Three Black Crows Pattern** - Bearish reversal pattern detection
5. **ADX (Average Directional Index)** - Trend strength measurement
6. **ADXR (Average Directional Index Rating)** - Trend stability indicator

### Key Functions and Patterns

#### TAAPI Integration (`modules/taapi.py`)
```python
# Individual indicator functions
fetch_rsi_taapi(symbol, taapi_key, interval="1m")
fetch_ma_taapi(symbol, taapi_key, period=20, interval="1m")
fetch_ema_taapi(symbol, taapi_key, period=12, interval="1m")
fetch_pattern_taapi(symbol, taapi_key, interval="1m")
fetch_adx_taapi(symbol, taapi_key, period=14, interval="1m")
fetch_adxr_taapi(symbol, taapi_key, period=14, interval="1m")

# Comprehensive indicator fetching
fetch_all_indicators(symbol, taapi_key, interval="1m")
```

#### Enhanced GPT Client (`modules/gpt_client.py`)
```python
# Enhanced function signature
ask_gpt_for_decision(openai_api_key, model, indicators, symbol, shares_owned, stock_price, wallet)

# Legacy compatibility
ask_gpt_for_decision_legacy(openai_api_key, model, rsi_value, symbol, shares_owned, stock_price, wallet)
```

#### Main Trading Logic (`trade_bot.py`)
```python
# Enhanced indicator fetching
fetch_all_technical_indicators(symbol) -> dict

# Enhanced trading cycle
run_once(api, symbol)  # Uses 6-indicator analysis with GPT fallback
```

## Configuration Management

### Environment Variables (.env)
```bash
# Core APIs
TAAPI_KEY=your_taapi_key
OPENAI_API_KEY=your_openai_key
ALPACA_API_KEY=your_alpaca_key
ALPACA_SECRET_KEY=your_alpaca_secret

# Trading Configuration
SYMBOLS=AAPL,TSLA,SPY
DRY_RUN=false
QTY=1

# Technical Indicator Periods
MA_PERIOD=20          # Moving Average period
EMA_PERIOD=12         # Exponential Moving Average period
ADX_PERIOD=14         # ADX calculation period
ADXR_PERIOD=14        # ADXR calculation period

# Optional: Discord notifications
DISCORD_WEBHOOK_URL=your_webhook_url
```

## AI Decision Making Process

### Enhanced GPT Prompt Structure
The system provides GPT with comprehensive market context:
- **6 technical indicators** with proper interpretation guidelines
- **Position & financial data** (current holdings, cash, stock price)
- **Risk management rules** (2% max risk per trade)
- **Trading guidelines** for confluence analysis between indicators

### Decision Flow
1. **Fetch all 6 technical indicators** from TAAPI.io
2. **Assemble comprehensive prompt** with indicator confluence analysis
3. **Query GPT-3.5-turbo** for trading decision with enhanced context
4. **Execute trade** (BUY/SELL/NOTHING) through Alpaca API
5. **Log decision & send notifications** via Discord webhook

## Development Guidelines

### When working with this codebase:

1. **Technical Indicators** - Always consider all 6 indicators when modifying analysis logic
2. **Error Handling** - The system has fallback from enhanced→RSI-only→graceful failure
3. **API Rate Limits** - 6x more TAAPI calls than original (18 calls/minute vs 3)
4. **Testing** - Use paper trading (ALPACA_BASE_URL=paper-api.alpaca.markets)
5. **Logging** - Comprehensive logging with technical indicator values for debugging

### Code Patterns to Follow

#### Error Handling Pattern
```python
try:
    indicators = fetch_all_technical_indicators(symbol)
    logger.info("Enhanced indicators for %s fetched successfully", symbol)
except Exception as e:
    logger.exception("Failed to fetch enhanced indicators for %s: %s", symbol, e)
    # Fallback to RSI-only mode
    try:
        rsi = fetch_rsi(symbol)
        indicators = {'rsi': rsi, 'ma': 'N/A', 'ema': 'N/A', 'pattern': 'N/A', 'adx': 'N/A', 'adxr': 'N/A'}
    except Exception as e2:
        logger.exception("Failed to fetch fallback RSI for %s: %s", symbol, e2)
        return
```

#### Indicator Validation Pattern
```python
# Always check for None values from TAAPI
if indicators.get('rsi') is None:
    indicators['rsi'] = 'N/A'
```

#### GPT Prompt Enhancement Pattern
```python
prompt = (
    f"TECHNICAL INDICATORS:\n"
    f"• RSI: {rsi} [Overbought >70, Oversold <30]\n"
    f"• MA: {ma} [Price vs MA indicates trend]\n"
    # ... include all 6 indicators with context
)
```

## Trading Strategy Logic

### Indicator Confluence Analysis
- **Trend Confirmation**: Price vs MA/EMA + ADX strength
- **Momentum Assessment**: RSI overbought/oversold levels
- **Pattern Recognition**: Three Black Crows for reversal signals
- **Trend Stability**: ADXR for trend reliability

### Risk Management
- **Maximum 2% risk per trade** (configured in GPT prompt)
- **Position sizing** based on available wallet balance
- **Stop-loss recommendations** included in GPT analysis

## Deployment & Operations

### Running the Enhanced Bot
```bash
python trade_bot.py  # Starts enhanced 6-indicator system
```

### Monitoring & Logs
- **File logging**: `log/TradeBot.MMDDYY.HH.log`
- **Discord notifications**: Real-time trade alerts and daily summaries
- **Technical indicator logging**: All 6 indicators logged per trading cycle

### Performance Considerations
- **API Rate Limits**: 6 TAAPI calls per symbol per cycle
- **Market Hours**: Automatic scheduling with pre-market and after-hours handling
- **Error Recovery**: Graceful degradation from enhanced→basic→skip cycle

## Migration Notes

### From Original RSI-Only System
- **Backward Compatible**: Legacy `ask_gpt_for_decision_legacy` function available
- **Enhanced Default**: New `ask_gpt_for_decision` uses 6-indicator analysis
- **Graceful Fallback**: System falls back to RSI-only if enhanced indicators fail

### API Changes
- **TAAPI Module**: Added 5 new indicator functions + `fetch_all_indicators`
- **GPT Client**: Enhanced prompt with 6-indicator confluence analysis
- **Main Bot**: Added `fetch_all_technical_indicators` wrapper function

This enhanced system provides significantly more sophisticated technical analysis while maintaining the reliability and error handling of the original RSI-only approach.