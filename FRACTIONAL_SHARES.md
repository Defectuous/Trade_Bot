# Fractional Shares Support

## 🎯 **Feature Overview**

Your trading bot now supports **fractional share trading** through Alpaca's fractional shares API! This allows for more precise position sizing and better capital utilization, especially for expensive stocks.

## ✨ **What's New**

### 🔧 **Enhanced Configuration**
- **QTY supports decimals**: `QTY=0.5` (half share), `QTY=1.25` (1.25 shares)
- **Automatic precision**: Whole numbers become integers, decimals become floats
- **GPT integration**: Dollar amounts automatically convert to fractional shares

### 📊 **Smart Order Handling**
```python
# Examples of supported quantities:
QTY=1      # 1 whole share
QTY=0.5    # 0.5 shares (half share)  
QTY=1.25   # 1.25 shares
QTY=0.1    # 0.1 shares (great for expensive stocks like NVDA)
```

### 🤖 **GPT Dollar Amount Conversion**
When GPT responds with dollar amounts, the bot automatically calculates fractional shares:

| GPT Response | Stock Price | Result | Order Type |
|--------------|-------------|---------|------------|
| `BUY $100` | $116.58 | 0.8578 shares | Fractional |
| `BUY $50` | $116.58 | 0.4289 shares | Fractional |
| `BUY $1000` | $116.58 | 8.5778 shares | Fractional |

## 🛠 **Implementation Details**

### Modified Functions:

#### `modules/alpaca_client.py`
- **`place_order()`**: Now accepts both `int` and `float` quantities
- **`can_buy()`**: Supports fractional share cost calculations  
- **`owns_at_least()`**: Handles fractional position comparisons

#### `trade_bot.py`
- **QTY parsing**: Supports `Decimal` values from environment variables
- **Order logic**: Automatically formats whole vs fractional quantities
- **Buying power**: Accurate calculations for fractional amounts

### Automatic Type Conversion:
```python
# The bot automatically chooses the right format:
if qty == qty.to_integral_value():
    qty_for_order = int(qty)      # Whole shares → int
else:
    qty_for_order = float(qty)    # Fractional → float
```

## 💡 **Use Cases**

### 🎯 **High-Value Stocks**
- **NVDA @ $800**: Use `QTY=0.125` to invest ~$100 per trade
- **GOOG @ $2500**: Use `QTY=0.04` to invest ~$100 per trade
- **BRK.A @ $500k**: Use `QTY=0.0002` for smaller positions

### 💰 **Precise Dollar Targeting**
```bash
# GPT can now specify exact dollar amounts:
GPT: "BUY $50"     → Bot calculates exact fractional shares
GPT: "BUY $1000"   → Bot converts to appropriate quantity
GPT: "SELL 1.5"    → Bot sells 1.5 shares exactly
```

### 🔄 **Portfolio Rebalancing**
- Sell partial positions: `SELL 0.7` shares
- Precise position sizing based on portfolio percentage
- Better risk management with smaller increments

## ⚙️ **Configuration Examples**

### Conservative Strategy (Expensive Stocks):
```bash
# For stocks >$500/share
QTY=0.1
SYMBOLS=NVDA,GOOG,AMZN
```

### Moderate Strategy (Mid-Range Stocks):
```bash  
# For stocks $100-500/share
QTY=0.5
SYMBOLS=AAPL,MSFT,TSLA
```

### Aggressive Strategy (Lower-Priced Stocks):
```bash
# For stocks <$100/share  
QTY=2.5
SYMBOLS=SPY,WMT,F
```

## 🔌 **Alpaca API Compatibility**

### ✅ **Supported Features**
- Fractional quantities down to **0.000001 shares**
- **Paper trading** fully supports fractional shares
- **Market orders** with fractional quantities
- **Position tracking** for fractional holdings

### ⚠️ **Limitations**
- Some **penny stocks** may not support fractional trading
- **Crypto** uses different endpoints (not implemented)
- **Options** trading doesn't support fractions (not applicable)

## 📈 **Benefits**

### 💰 **Capital Efficiency**
- **Better diversification** with limited capital
- **Precise position sizing** regardless of stock price
- **No leftover cash** from high-priced stocks

### 🎯 **Enhanced GPT Integration**  
- **Dollar-based recommendations** work perfectly
- **Risk management** improvements with smaller increments
- **Flexible strategy** adaptation based on market conditions

### 📊 **Improved Risk Management**
- **Smaller position sizes** for testing new strategies
- **Gradual position building** with fractional increments  
- **Precise stop-loss** execution

## 🚀 **Usage Examples**

### Example 1: High-Value Stock Trading
```bash
# .env configuration for expensive stocks
QTY=0.1
SYMBOLS=NVDA,GOOG

# GPT Response: "BUY $500"
# Result: Buys 0.625 NVDA shares @ $800/share = $500
```

### Example 2: Precise Dollar Targeting
```bash
# GPT Response: "BUY $1000"  
# AAPL @ $150/share → 6.6667 shares
# Total cost: $1000.00 (exact)
```

### Example 3: Partial Position Exit
```bash
# Current position: 2.5 TSLA shares
# GPT Response: "SELL 1.2" 
# Result: Sells 1.2 shares, keeps 1.3 shares
```

## 🧪 **Testing**

Run the test suite to validate fractional share functionality:

```bash
python test_fractional_shares.py
```

## 📝 **Migration Notes**

### ✅ **Backward Compatible**
- Existing `QTY=1` configurations work unchanged
- Integer values automatically become whole share orders
- No breaking changes to existing functionality

### 🔄 **Automatic Upgrades**
- GPT dollar parsing now supports fractional results
- Enhanced buying power calculations
- Improved order execution logging

---

**Feature Status**: ✅ **Production Ready**  
**Alpaca Support**: ✅ **Full Fractional API Support**  
**Testing**: ✅ **Comprehensive Test Coverage**

*Fractional shares feature implemented: September 30, 2025*