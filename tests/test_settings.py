"""settings 모듈 테스트 — 네트워크 없이 동작해야 한다."""

from pathlib import Path

import pytest

from plick_embedding.settings import load_settings

MISSING_ENV = Path("/nonexistent/.env")


def test_load_settings_from_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")

    settings = load_settings(env_file=MISSING_ENV)

    assert settings.has_gemini
    assert settings.has_openai


def test_missing_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    settings = load_settings(env_file=MISSING_ENV)

    assert not settings.has_gemini
    assert not settings.has_openai
    assert "없음" in settings.summary()


def test_summary_does_not_leak_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "secret-value-123")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    settings = load_settings(env_file=MISSING_ENV)

    assert "secret-value-123" not in settings.summary()
