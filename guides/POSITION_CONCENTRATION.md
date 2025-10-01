# Position Concentration Risk Management

## Overview

The trading bot now includes comprehensive position concentration risk management to prevent over-investing in any single stock. This feature helps maintain portfolio diversification and reduces risk.

## Features

### 1. Portfolio Percentage Limits
- **Default**: Maximum 20% of portfolio value in any single stock
- **Configurable**: Adjust via `MAX_POSITION_VALUE_PCT` environment variable
- **Dynamic**: Calculated based on real-time portfolio value

### 2. Absolute Share Limits  
- **Default**: Maximum 100 shares of any single stock
- **Configurable**: Adjust via `MAX_POSITION_SHARES` environment variable
- **Protection**: Prevents accidentally accumulating too many shares

### 3. Smart Position Adjustment
- **Automatic**: Reduces order size to stay within limits
- **Transparent**: Logs adjustments with clear explanations
- **Safe**: Blocks orders that would exceed limits even after adjustment

## Configuration

### Environment Variables

```bash
# Enable/disable position concentration limits
ENABLE_POSITION_LIMITS=true

# Maximum percentage of portfolio in single stock (default: 20%)
MAX_POSITION_VALUE_PCT=20

# Maximum absolute shares per stock (default: 100)
MAX_POSITION_SHARES=100
```

### Recommended Settings by Account Size

#### Small Accounts ($100-$1,000)
```bash
MAX_POSITION_VALUE_PCT=25    # Allow higher concentration (limited diversification options)
MAX_POSITION_SHARES=20       # Lower absolute limits for expensive stocks
ENABLE_POSITION_LIMITS=true
```

#### Medium Accounts ($1,000-$10,000)  
```bash
MAX_POSITION_VALUE_PCT=20    # Balanced approach
MAX_POSITION_SHARES=50       # Moderate share limits
ENABLE_POSITION_LIMITS=true
```

#### Large Accounts ($10,000+)
```bash
MAX_POSITION_VALUE_PCT=15    # Conservative for better diversification
MAX_POSITION_SHARES=100      # Higher absolute limits
ENABLE_POSITION_LIMITS=true
```

## How It Works

### Example Scenario

**Portfolio**: $10,000 total value  
**Current AAPL position**: 10 shares @ $150 = $1,500 (15% of portfolio)  
**GPT recommendation**: BUY $1,000 worth (≈6.67 shares)  
**Proposed position**: 16.67 shares @ $150 = $2,500 (25% of portfolio)

### Risk Check Process

1. **Calculate proposed position**: 16.67 shares × $150 = $2,500
2. **Check percentage limit**: $2,500 ÷ $10,000 = 25% > 20% limit ❌
3. **Calculate maximum allowed**: $10,000 × 20% = $2,000 max position
4. **Determine adjustment**: $2,000 ÷ $150 = 13.33 max shares
5. **Adjust order**: 13.33 - 10 = 3.33 shares allowed
6. **Execute**: BUY 3.33 shares (adjusted from 6.67)

### Logging Output

```
📊 Position adjusted for concentration limits: 3.33 shares for AAPL
🛡️ Reason: Adjusted to stay within 20.0% portfolio limit
```

## Benefits

### 1. **Risk Reduction**
- Prevents over-concentration in single stocks
- Maintains portfolio diversification
- Reduces impact of individual stock volatility

### 2. **Automatic Protection**
- No manual intervention required
- Works with GPT recommendations
- Transparent logging for audit trail

### 3. **Flexible Configuration**
- Adapt to different account sizes
- Adjust for risk tolerance
- Enable/disable as needed

### 4. **Smart Integration**
- Works with existing GPT decision making
- Compatible with fractional shares
- Respects existing fund checking logic

## Advanced Configuration Examples

### Conservative Portfolio (Low Risk)
```bash
MAX_POSITION_VALUE_PCT=10    # Very conservative 10% limit
MAX_POSITION_SHARES=25       # Lower share limits
ENABLE_POSITION_LIMITS=true
```

### Aggressive Growth (Higher Risk)
```bash
MAX_POSITION_VALUE_PCT=30    # Allow higher concentration
MAX_POSITION_SHARES=200      # Higher share limits  
ENABLE_POSITION_LIMITS=true
```

### Disable Limits (For Testing)
```bash
ENABLE_POSITION_LIMITS=false  # Turn off all position limits
```

## Error Handling

The system includes robust error handling:

- **API Failures**: Continues with purchase if position check fails
- **Missing Data**: Uses conservative defaults
- **Invalid Values**: Logs warnings and uses safe fallbacks
- **Edge Cases**: Handles zero/negative values gracefully

## Integration with Other Features

### Works With:
- ✅ GPT trading decisions
- ✅ Fund checking and safety margins
- ✅ Fractional share support
- ✅ Multiple symbol trading
- ✅ Discord notifications

### Execution Order:
1. GPT makes trading recommendation
2. Position concentration check (NEW)
3. Fund availability check
4. Fractional share compatibility check
5. Order execution

## Monitoring

### Key Log Messages

```bash
# Normal operation
📊 Position adjusted for concentration limits: 5.5 shares for TSLA
🛡️ Reason: Adjusted to stay within 20.0% portfolio limit

# Blocked purchases
🚫 Position concentration limit reached for NVDA: Already own 100 shares, max allowed is 100

# Error conditions
⚠️ Could not check position concentration for AAPL: API error. Proceeding with original order.
```

This feature provides institutional-grade risk management while maintaining the bot's automated trading capabilities.