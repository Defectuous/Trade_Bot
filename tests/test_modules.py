import pytest
from decimal import Decimal

from modules.gpt_client import ask_gpt_for_decision
from modules.alpaca_client import get_owned_positions


def test_taapi_integration():
    """Test that TAAPI module functions are available."""
    from modules.taapi import fetch_rsi_taapi, fetch_all_indicators
    # Just test that functions are importable
    assert callable(fetch_rsi_taapi)
    assert callable(fetch_all_indicators)


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
