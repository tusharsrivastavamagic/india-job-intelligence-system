import os
from job_intelligence.config import load_settings
def test_gemini_key_is_loaded_without_exposing_value(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY","test-key")
    assert load_settings().gemini_api_key == "test-key"
def test_apify_tokens_prioritize_multi_token_setting(monkeypatch):
    monkeypatch.setenv("APIFY_TOKEN","legacy")
    monkeypatch.setenv("APIFY_TOKENS"," first, , second , ")
    assert load_settings().apify_tokens == ("first","second")
