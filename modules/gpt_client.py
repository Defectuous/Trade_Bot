"""GPT client wrapper (OpenAI).

Provides a single function to ask the trading decision question. Logs prompt and raw reply
for auditing. Designed to be resilient to OpenAI client differences (chat vs completions).
"""
from decimal import Decimal
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

try:
    import openai
except Exception:
    openai = None


def ask_gpt_for_decision(openai_api_key: str, model: str, rsi_value: Decimal, symbol: str, shares_owned: Decimal, stock_price: Decimal, wallet: Decimal) -> Tuple[str, Optional[Decimal]]:
    """Ask GPT for a decision. Returns (action, amount).

    action is one of 'BUY', 'SELL', 'NOTHING'. amount is Decimal or None.
    """
    if not openai_api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    if openai is None:
        raise RuntimeError("openai package not installed")

    Client = getattr(openai, "OpenAI", None)
    if Client is None:
        raise RuntimeError("openai package does not expose OpenAI client; please install openai>=1.0.0")

    prompt = (
        "You are an expert stock trader specializing in day trading and you have been tasked with reviewing the following information of a stock: "
        f"Relative Strength Index (RSI)={rsi_value}, the current price of the stock [Stock_Price]={stock_price}, how many shares of this stock you currently own [Shares_Owned_Of_Stock]={shares_owned}, "
        f"and how much money is available [Wallet]={wallet}. The overbought threshold is 70 and the oversold threshold is 30. "
        "Your goal is to maximize profit while adhering to strict risk management. Your risk tolerance is a maximum of 2% of your wallet per trade. "
        "If a trade is executed, a stop-loss should be set at a price that limits potential loss to this amount. "
        "Please reply with exactly one of the following: BUY [Amount], SELL [Amount], NOTHING."
    )

    logger.debug("GPT prompt: %s", prompt)

    client = Client(api_key=openai_api_key)

    text = None
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=40,
            temperature=0,
        )
        try:
            text = resp.choices[0].message.content.strip()
        except Exception:
            try:
                text = resp["choices"][0]["message"]["content"].strip()
            except Exception:
                text = str(resp).strip()
    except Exception as e:
        logger.debug("Chat completions call failed: %s", e)
        # try legacy completions
        try:
            resp2 = client.completions.create(model=model, prompt=prompt, max_tokens=40, temperature=0)
            try:
                text = resp2.choices[0].text.strip()
            except Exception:
                text = str(resp2).strip()
        except Exception:
            logger.exception("GPT API call failed")
            raise

    logger.info("GPT raw reply: %s", text)

    if not text:
        return "NOTHING", None

    parts = text.strip().split()
    if not parts:
        return "NOTHING", None
    action = parts[0].upper()
    amount = None
    if action not in ("BUY", "SELL", "NOTHING"):
        return "NOTHING", None
    if action in ("BUY", "SELL") and len(parts) >= 2:
        try:
            amount = Decimal(parts[1])
        except Exception:
            cleaned = ''.join(c for c in parts[1] if (c.isdigit() or c in '.-'))
            try:
                amount = Decimal(cleaned) if cleaned else None
            except Exception:
                amount = None

    return action, amount
"""GPT client wrapper (OpenAI).

Provides a single function to ask the trading decision question. Logs prompt and raw reply
for auditing. Designed to be resilient to OpenAI client differences (chat vs completions).
"""
from decimal import Decimal
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

try:
    import openai
except Exception:
    openai = None


def ask_gpt_for_decision(openai_api_key: str, model: str, rsi_value: Decimal, symbol: str, shares_owned: Decimal, stock_price: Decimal, wallet: Decimal) -> Tuple[str, Optional[Decimal]]:
    """Ask GPT for a decision. Returns (action, amount).

    action is one of 'BUY', 'SELL', 'NOTHING'. amount is Decimal or None.
    """
    if not openai_api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    if openai is None:
        raise RuntimeError("openai package not installed")

    Client = getattr(openai, "OpenAI", None)
    if Client is None:
        raise RuntimeError("openai package does not expose OpenAI client; please install openai>=1.0.0")

    prompt = (
        "You are an expert stock trader specializing in day trading and you have been tasked with reviewing the following information of a stock.: "
        f"The Relative Strength Index (RSI)={rsi_value}, the current price of the stock [Stock_Price]={stock_price}, how many shares of this stock you currently own [Shares_Owned_Of_Stock]={shares_owned}, "
        f"and how much money is available [Wallet]={wallet}. The overbought threshold is 70 and the oversold threshold is 30. "
        "Your goal is to maximize profit while adhering to strict risk management. Your risk tolerance is a maximum of 2% of your wallet per trade. "
        "If a trade is executed, a stop-loss should be set at a price that limits potential loss to this amount. "
        "Please reply with exactly one of the following: BUY [Amount], SELL [Amount], NOTHING."
    )

    logger.debug("GPT prompt: %s", prompt)

    client = Client(api_key=openai_api_key)

    resp = None
    text = None
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=40,
            temperature=0,
        )
        try:
            text = resp.choices[0].message.content.strip()
        except Exception:
            try:
                text = resp["choices"][0]["message"]["content"].strip()
            except Exception:
                text = str(resp).strip()
    except Exception as e:
        logger.debug("Chat completions call failed: %s", e)
        # try legacy completions
        try:
            resp2 = client.completions.create(model=model, prompt=prompt, max_tokens=40, temperature=0)
            try:
                text = resp2.choices[0].text.strip()
            except Exception:
                text = str(resp2).strip()
        except Exception:
            logger.exception("GPT API call failed")
            raise

    logger.info("GPT raw reply: %s", text)

    if not text:
        return "NOTHING", None

    parts = text.split()
    if not parts:
        return "NOTHING", None
    action = parts[0].upper()
    amount = None
    if action not in ("BUY", "SELL", "NOTHING"):
        return "NOTHING", None
    if action in ("BUY", "SELL") and len(parts) >= 2:
        try:
            amount = Decimal(parts[1])
        except Exception:
            cleaned = ''.join(c for c in parts[1] if (c.isdigit() or c in '.-'))
            try:
                amount = Decimal(cleaned) if cleaned else None
            except Exception:
                amount = None

    return action, amount
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

try:
    import openai
except Exception:
    openai = None


def ask_gpt_for_decision_extended(openai_api_key: str, model: str, rsi_value: Decimal, symbol: str, shares_owned: Decimal, stock_price: Decimal, wallet: Decimal):
    """
    Wrapper that calls OpenAI and returns (action, amount) similar to previous function.
    """
    if not openai_api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    if openai is None:
        raise RuntimeError("openai package not installed")

    Client = getattr(openai, "OpenAI", None)
    if Client is None:
        raise RuntimeError("openai package does not expose OpenAI client; please install openai>=1.0.0")

    prompt = (
        "You are an expert stock trader specializing in day trading and you have been tasked with reviewing the following information of a stock: "
        f"Relative Strength Index (RSI)={rsi_value}, the current price of the stock [Stock_Price]={stock_price}, how many shares of this stock you currently own [Shares_Owned_Of_Stock]={shares_owned}, "
        f"and how much money is available [Wallet]={wallet}. The overbought threshold is 70 and the oversold threshold is 30. "
        "Your goal is to maximize profit while adhering to strict risk management. Your risk tolerance is a maximum of 2% of your wallet per trade. "
        "If a trade is executed, a stop-loss should be set at a price that limits potential loss to this amount. "
        "Please reply with exactly one of the following: BUY [Amount], SELL [Amount], NOTHING."
    )

    client = Client(api_key=openai_api_key)
    try:
        logger.debug("GPT prompt: %s", prompt)
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20,
            temperature=0,
        )
    except Exception:
        err = None
        try:
            raise
        except Exception as e:
            err = e
        msg = str(err)
        if "not a chat model" in msg or "v1/chat/completions" in msg:
            try:
                resp2 = client.completions.create(
                    model=model,
                    prompt=prompt,
                    max_tokens=20,
                    temperature=0,
                )
                try:
                    text = resp2.choices[0].text.strip()
                except Exception:
                    text = str(resp2).strip()
            except Exception:
                logger.exception("Fallback completions API call failed")
                raise
        else:
            logger.exception("GPT API call failed")
            raise

    if 'text' not in locals() or not locals().get('text'):
        try:
            text = resp.choices[0].message.content.strip()
        except Exception:
            try:
                text = resp["choices"][0]["message"]["content"].strip()
            except Exception:
                text = str(resp).strip()

    logger.info("GPT raw reply: %s", text)

    parts = text.strip().split()
    if not parts:
        logger.warning("GPT returned empty reply")
        return "NOTHING", None

    action = parts[0].upper()
    amount = None
    if action not in ("BUY", "SELL", "NOTHING"):
        logger.warning("GPT returned unexpected action: %s", text)
        return "NOTHING", None

    if action in ("BUY", "SELL") and len(parts) >= 2:
        try:
            amount = Decimal(parts[1])
        except Exception:
            cleaned = ''.join(c for c in parts[1] if (c.isdigit() or c in '.-'))
            try:
                amount = Decimal(cleaned) if cleaned else None
            except Exception:
                amount = None

    return action, amount
