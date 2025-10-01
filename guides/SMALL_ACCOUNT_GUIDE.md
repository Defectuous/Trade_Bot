# Small Account Configuration Guide

## 🎯 **Your $100 Account - Optimized Settings**

Based on your $100 budget, here are the recommended settings for safe and effective trading:

### 📋 **Recommended .env Configuration**

```bash
# Conservative settings for $100 account
QTY=0.1                    # Very small fractional shares
DRY_RUN=true              # Keep testing until confident
SYMBOLS=SPY,AAPL          # Focus on 1-2 liquid stocks

# Enable only essential indicators to reduce API costs
ENABLE_RSI=true           # Core momentum indicator
ENABLE_MA=true            # Trend direction
ENABLE_EMA=false          # Disable to save API calls
ENABLE_PATTERN=false      # Disable to save API calls  
ENABLE_ADX=false          # Disable to save API calls
ENABLE_ADXR=false         # Disable to save API calls
```

### 💰 **Position Sizing Strategy**

| Stock Price Range | Recommended QTY | Trade Size | Rationale |
|-------------------|-----------------|------------|-----------|
| $50-100 (SPY)    | QTY=0.5        | ~$25-50   | Good starter position |
| $100-200 (AAPL)  | QTY=0.25       | ~$25-50   | Conservative for growth stocks |
| $200+ (TSLA)      | QTY=0.1        | ~$20-50   | Very small positions |

### 🛡️ **Safety Features Now Active**

With the latest updates, your bot now includes:

1. **🚨 Small Account Alerts**: GPT receives special warnings about your $100 budget
2. **💰 Automatic Capping**: Orders automatically limited to available cash
3. **📊 Enhanced Logging**: Clear visibility into wallet amounts and safety checks
4. **🎯 Conservative Prompts**: GPT guided toward $10-50 trade recommendations

### 📈 **Expected Trading Pattern**

With $100 budget and these safety features:

```
Example Scenario:
- Available: $100
- Stock: AAPL @ $150
- GPT might suggest: "BUY $2000" (without safety)
- Safety check caps to: 0.67 shares ($100 max)
- Actual order: 0.67 AAPL shares = $100.50
```

### 🔄 **Growth Strategy**

As your account grows, adjust settings:

#### **$100 → $500 (5x growth)**
```bash
QTY=0.5                   # Increase position sizes
ENABLE_EMA=true          # Add back indicators
SYMBOLS=SPY,AAPL,MSFT    # Diversify to 3 stocks
```

#### **$500 → $1000 (10x growth)**
```bash
QTY=1.0                  # Whole share positions
ENABLE_ADX=true          # Full indicator suite
SYMBOLS=SPY,AAPL,MSFT,TSLA  # 4-stock portfolio
```

### 🎯 **Risk Management**

For your $100 account:
- **Max loss per trade**: $2 (2% rule)
- **Recommended trade size**: $10-50
- **Daily loss limit**: $10 (10% of account)
- **Position limit**: 1-2 stocks max

### 📊 **API Cost Optimization**

With reduced indicators (RSI + MA only):
- **TAAPI calls**: ~2 per minute vs 6 (67% savings)
- **Monthly cost**: ~$5-10 vs $15-20
- **Still effective**: RSI + MA provides solid signals

### ⚙️ **Testing Protocol**

Before going live with real money:

1. **Paper Trading**: Test with `DRY_RUN=true` for 1-2 weeks
2. **Monitor Logs**: Verify safety checks are working
3. **Check Recommendations**: Ensure GPT suggests reasonable amounts
4. **Gradual Increase**: Start with $25 trades, then increase

### 🚨 **Red Flags to Watch**

Stop trading if you see:
- GPT consistently recommending >$100 amounts
- Safety checks not triggering when they should  
- Orders being placed for >$100
- Account balance not updating correctly

---

**With these safety features, your $100 account is now protected from over-trading while still allowing for meaningful position building!** 🎯