from decimal import Decimal, getcontext
import re

getcontext().prec = 12

# Local copy of compute_rsi_from_closes (Wilder smoothing)
def compute_rsi_from_closes(closes, period=14):
    if len(closes) < period + 1:
        raise ValueError("Not enough data points to compute RSI")
    closes = [Decimal(str(c)) for c in closes]
    gains = []
    losses = []
    for i in range(1, len(closes)):
        change = closes[i] - closes[i - 1]
        if change > 0:
            gains.append(change)
            losses.append(Decimal('0'))
        else:
            gains.append(Decimal('0'))
            losses.append(abs(change))
    # initial average
    avg_gain = sum(gains[:period]) / Decimal(period)
    avg_loss = sum(losses[:period]) / Decimal(period)
    # Wilder smoothing for the rest
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / Decimal(period)
        avg_loss = (avg_loss * (period - 1) + losses[i]) / Decimal(period)
    if avg_loss == 0:
        return Decimal('100')
    rs = avg_gain / avg_loss
    rsi = Decimal('100') - (Decimal('100') / (Decimal('1') + rs))
    return rsi

# Positions parsing helper similar to modules.alpaca_client.get_owned_positions
def parse_owned_positions(positions):
    out = {}
    for p in positions:
        if isinstance(p, dict):
            symbol = p.get('symbol')
            qty = p.get('qty')
        else:
            # object with attributes
            symbol = getattr(p, 'symbol', None)
            qty = getattr(p, 'qty', None)
        if symbol is None or qty is None:
            continue
        try:
            qty_dec = Decimal(str(qty))
        except Exception:
            try:
                qty_dec = Decimal(qty)
            except Exception:
                continue
        out[symbol] = qty_dec
    return out

# Minimal GPT reply parser similar to the bot's expectations
RE_ACTION = re.compile(r"\b(BUY|SELL|HOLD)\b", re.I)
RE_AMOUNT = re.compile(r"([-+]?\d*\.?\d+)")

def parse_gpt_reply(text):
    text = (text or "").strip()
    m = RE_ACTION.search(text)
    action = m.group(1).upper() if m else 'HOLD'
    amt = Decimal('0')
    m2 = RE_AMOUNT.search(text)
    if m2:
        try:
            amt = Decimal(m2.group(1))
        except Exception:
            amt = Decimal('0')
    return action, amt


if __name__ == '__main__':
    print('Running local smoke_test')

    # Test RSI with sample closes
    closes = [44.34,44.09,44.15,43.61,44.33,44.83,45.10,45.42,45.84,46.08,45.89,46.03,45.61,46.28,46.28]
    try:
        rsi = compute_rsi_from_closes(closes, period=14)
        print('RSI computed:', rsi)
    except Exception as e:
        print('RSI test failed:', e)

    # Test positions parsing
    class FakePos:
        def __init__(self, symbol, qty):
            self.symbol = symbol
            self.qty = qty

    fake_positions = [FakePos('AAPL', '2'), {'symbol': 'TSLA', 'qty': '1.5'}, {'symbol': 'BAD', 'qty': 'n/a'}]
    owned = parse_owned_positions(fake_positions)
    print('Owned positions:', owned)

    # Test GPT parsing
    for sample in ['BUY 3', 'sell 1.5 shares', 'HOLD', 'I recommend BUY 2', 'action: SELL amount: 4.0', 'no trade']:
        a, q = parse_gpt_reply(sample)
        print('Reply:', sample, '->', a, q)

    print('Smoke test completed')
