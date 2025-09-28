Purpose

This repository is a small trading-bot scaffold that: (1) fetches a 1-minute RSI from TAAPI.io, (2) asks an OpenAI chat model to return one of `BUY`, `SELL`, or `NOTHING` for that RSI, and (3) places market orders via the Alpaca Python SDK (paper by default).

Quick Entry Points

- **Entry file:** `trade_bot.py` — main loop, minute cadence, market-hours gating.
- **Deps:** `requirements.txt` — install in a Python 3.9+ venv.
- **Config example:** `.env.example` — copy to `.env` and fill secrets.
- **Docs:** `README.md` — quickstart and run commands.

Important Files & Responsibilities

- `trade_bot.py`:
  - **`fetch_rsi(symbol)`**: calls `https://api.taapi.io/rsi` with `secret=TAAPI_KEY`; expects JSON with `value` (RSI).
  - **`ask_gpt_for_decision(rsi)`**: builds a one-shot prompt and uses OpenAI ChatCompletion; expects a single-token reply `BUY/SELL/NOTHING` (uppercased).
  - **`connect_alpaca()` / `place_order()` / `owns_at_least()` / `can_buy()`**: thin wrappers around `alpaca_trade_api.REST`.
  - **`main()`**: enforces US/Eastern market hours (09:30–16:00 ET) and sleeps to the next full minute.

Key Project Conventions (be explicit)

- Timezone: market gating uses `pytz` `US/Eastern`. Treat all trading times in ET.
- Money/precision: use `Decimal` for RSI/price arithmetic; keep conversions explicit.
- GPT contract: code normalizes model output to the first token and treats anything unexpected as `NOTHING`. Any change to the prompt or parsing must update both the prompt text and the normalization logic.
- DRY_RUN: toggled with `DRY_RUN` env var (default `true` in `.env.example`). When `DRY_RUN` is true the code will log intended orders but not submit them.
- Alpaca: default `ALPACA_BASE_URL` is paper endpoint. Switch explicitly for live trading.

Environment Variables (discoverable)

- `TAAPI_KEY` — TAAPI.io secret.
- `OPENAI_API_KEY` — OpenAI API key.
- `OPENAI_MODEL` — defaults to `gpt-3.5-turbo-instruct` (overridable).
- `ALPACA_API_KEY`, `ALPACA_SECRET_KEY`, `ALPACA_BASE_URL` — Alpaca credentials & endpoint.
- `SYMBOL` — ticker (default `AAPL`).
- `QTY` — integer share quantity to trade.
- `DRY_RUN` — `true|false` to avoid live orders.
- `LOG_LEVEL` — logging level.

Network & Integration Notes

- TAAPI call format (example):
  `https://api.taapi.io/rsi?symbol=AAPL&interval=1m&type=stocks&secret=<TAAPI_KEY>` — response must include `value`.
- OpenAI usage: uses ChatCompletion.create with `messages=[{"role":"user","content": prompt}]`. The prompt asks for exactly one of `BUY/SELL/NOTHING` — code enforces this.
- Alpaca SDK calls used in code: `get_account()`, `get_position(symbol)`, `submit_order(...)`, `get_last_trade(symbol)`, `get_barset(symbol, '1Min', limit=1)`.

Testing, Debugging & Safe Experimentation

- Always run with `DRY_RUN=true` and Alpaca paper account first.
- Useful unit-test targets:
  - `fetch_rsi()` — mock `requests.get` and validate Decimal parsing and error handling.
  - `ask_gpt_for_decision()` — mock `openai.ChatCompletion.create` to test parsing of different replies.
  - `place_order()` / `owns_at_least()` — mock Alpaca REST client.
- When debugging timing issues, inspect the sleep logic in `main()` (it aligns to the next full minute).

Editing Guidelines for Contributors / AI Agents

- If you modify the GPT prompt, update the parsing logic together — the code assumes single-token decisions.
- Keep `DRY_RUN` default to `true` in examples and CI; do not commit live keys.
- Preserve UTC/ET handling: if changing timezone behavior, document why and update README.
- Add unit tests when changing integrations (mock external HTTP and SDK calls).

Run Commands (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
#$env:DRY_RUN = "true"; python .\trade_bot.py
```

Examples (from code)

- Prompt sent to OpenAI:
  "You are an expert stock trader ... The stock RSI value is 34.12. Please reply with exactly one of: BUY, SELL, NOTHING."
- TAAPI expected JSON: `{"value": 34.12, ...}` — code reads `data['value']` and casts to `Decimal`.

Security

- Never store secrets in source. Use `.env` locally or your CI/secret manager. `.env.example` shows the required keys.

If Anything Is Unclear

- Ask the maintainer for missing environment details or for expected Alpaca account type. If you need test credentials, request a paper-account key and enable `DRY_RUN`.