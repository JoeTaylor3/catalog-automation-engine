import os

import pytest

from ai.llm_summary import generate_ai_summary


class DummyResponse:
    def __init__(self, text):
        self.choices = [{"message": {"content": text}}]


class DummyChat:
    @staticmethod
    def create(*args, **kwargs):
        # ignore args; return a simple canned response
        return DummyResponse("Executive summary text.")


@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    # ensure OPENAI_API_KEY is set for the duration of the test
    monkeypatch.setenv("OPENAI_API_KEY", "fake-key")
    # replace openai.ChatCompletion with dummy
    import openai

    monkeypatch.setattr(openai, "ChatCompletion", DummyChat)


def test_generate_ai_summary_basic():
    metrics = {"total_records": 1000, "invalid_pct": 2.5}
    sql_insights = {
        "duplicate_sku_count": 5,
        "high_price_anomalies": 3,
        "low_inventory_warnings": 10,
    }
    validation_summary = {"top_issue_types": ["missing_price", "bad_sku"]}

    summary = generate_ai_summary(metrics, sql_insights, validation_summary)
    assert "Executive summary text." in summary


def test_missing_api_key_raises(monkeypatch):
    # clear the key
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError):
        generate_ai_summary({}, {}, {})
