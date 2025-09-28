import pytest
from decimal import Decimal

from modules.alpaca_rsi import compute_rsi_from_closes
from modules.gpt_client import ask_gpt_for_decision_extended
from modules.alpaca_client import get_owned_positions


def test_compute_rsi_simple():
    # Construct a sequence of prices that will result in a known RSI
    closes = [44.34,44.09,44.15,43.61,44.33,44.83,45.10,45.42,45.84,46.08,45.89,46.03,45.61,46.28,46.28]
    # Using period=14, these are the first 15 closes from classic RSI example; ensure function runs
    rsi = compute_rsi_from_closes(closes, period=14)
    assert isinstance(rsi, Decimal)
    assert rsi >= 0 and rsi <= 100


class DummyOpenAIClient:
    class Chat:
        @staticmethod
        def completions_create(**kwargs):
            class Resp:
                choices = [type('o', (), {'message': type('m', (), {'content': 'BUY 2'})})()]
            return Resp()

    def __init__(self, api_key=None):
        class C:
            def __init__(self):
                self.chat = type('chat', (), {'completions': type('c', (), {'create': DummyOpenAIClient.Chat.completions_create})()})()
        self._c = C()


def test_gpt_parsing(monkeypatch):
    # Monkeypatch openai.OpenAI to return our dummy client
    import modules.gpt_client as gpt
    class DummyOpenAI:
        def __init__(self, api_key=None):
            self.chat = type('chat', (), {'completions': type('c', (), {'create': lambda *a, **k: type('r', (), {'choices': [type('x', (), {'message': type('m', (), {'content': 'BUY 3'})})()]})()})()})()
    monkeypatch.setattr(gpt, 'openai', type('o', (), {'OpenAI': DummyOpenAI}))

    action, amount = gpt.ask_gpt_for_decision_extended('key', 'model', Decimal('50'), 'AAPL', Decimal('0'), Decimal('150.0'), Decimal('1000'))
    assert action in ('BUY', 'SELL', 'NOTHING')
    # amount may be parsed


def test_get_owned_positions_with_dummy_api():
    class FakePos:
        def __init__(self, symbol, qty):
            self.symbol = symbol
            self.qty = qty

    class FakeAPI:
        def list_positions(self):
            return [FakePos('AAPL', '2'), {'symbol': 'TSLA', 'qty': '1.5'}]

    api = FakeAPI()
    owned = get_owned_positions(api)
    assert owned['AAPL'] == Decimal('2')
    assert owned['TSLA'] == Decimal('1.5')
