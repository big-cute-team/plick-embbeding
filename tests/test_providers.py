"""providers 테스트 — 캐시·정규화·재시도. 네트워크 없이 동작해야 한다."""

from pathlib import Path

import numpy as np
import pytest

from plick_embedding.providers import gemini as gemini_module
from plick_embedding.providers.base import EmbeddingConfig, l2_normalize
from plick_embedding.providers.cache import EmbeddingCache
from plick_embedding.providers.gemini import MAX_RETRIES, GeminiEmbeddingProvider
from plick_embedding.providers.openai import OpenAIEmbeddingProvider

CONFIG = EmbeddingConfig(model="test-model", task_type="SEMANTIC_SIMILARITY", dim=4)
OPENAI_CONFIG = EmbeddingConfig(model="text-embedding-3-small", task_type="none", dim=4)


def test_l2_normalize_unit_length() -> None:
    vectors = np.array([[3.0, 4.0], [0.0, 0.0]])
    normalized = l2_normalize(vectors)
    assert np.allclose(np.linalg.norm(normalized[0]), 1.0)
    assert np.allclose(normalized[1], 0.0)  # 영벡터는 그대로


def test_cache_roundtrip(tmp_path: Path) -> None:
    cache = EmbeddingCache(cache_dir=tmp_path)
    vector = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)

    assert cache.get("텍스트", CONFIG) is None
    cache.put("텍스트", CONFIG, vector)
    assert np.allclose(cache.get("텍스트", CONFIG), vector)


def test_cache_key_includes_config(tmp_path: Path) -> None:
    cache = EmbeddingCache(cache_dir=tmp_path)
    cache.put("텍스트", CONFIG, np.ones(4, dtype=np.float32))

    other = EmbeddingConfig(model="test-model", task_type="CLUSTERING", dim=4)
    assert cache.get("텍스트", other) is None


def test_gemini_provider_uses_cache_without_api(tmp_path: Path) -> None:
    """모든 텍스트가 캐시에 있으면 API 클라이언트를 만들지 않는다."""
    cache = EmbeddingCache(cache_dir=tmp_path)
    texts = ["기사 하나", "기사 둘"]
    for i, text in enumerate(texts):
        vector = np.zeros(4, dtype=np.float32)
        vector[i] = 1.0
        cache.put(text, CONFIG, vector)

    provider = GeminiEmbeddingProvider(CONFIG, api_key="fake-key", cache=cache)
    result = provider.embed(texts)

    assert result.shape == (2, 4)
    assert provider._client is None  # API 호출 없음
    assert np.allclose(result[0], [1, 0, 0, 0])
    assert np.allclose(result[1], [0, 1, 0, 0])


def test_openai_provider_uses_cache_without_api(tmp_path: Path) -> None:
    """OpenAI도 모든 텍스트가 캐시에 있으면 API 클라이언트를 만들지 않는다."""
    cache = EmbeddingCache(cache_dir=tmp_path)
    texts = ["기사 하나", "기사 둘"]
    for i, text in enumerate(texts):
        vector = np.zeros(4, dtype=np.float32)
        vector[i] = 1.0
        cache.put(text, OPENAI_CONFIG, vector)

    provider = OpenAIEmbeddingProvider(OPENAI_CONFIG, api_key="fake-key", cache=cache)
    result = provider.embed(texts)

    assert result.shape == (2, 4)
    assert provider._client is None  # API 호출 없음
    assert np.allclose(result[0], [1, 0, 0, 0])


class _FakeEmbedding:
    def __init__(self, values: list[float]) -> None:
        self.values = values


class _FakeResponse:
    def __init__(self, count: int) -> None:
        self.embeddings = [_FakeEmbedding([1.0, 0.0, 0.0, 0.0]) for _ in range(count)]


class _FlakyGeminiClient:
    """정해진 횟수만큼 실패한 뒤 성공하는 가짜 Gemini 클라이언트."""

    def __init__(self, fails: int) -> None:
        self.fails = fails
        self.calls = 0
        self.models = self

    def embed_content(self, model, contents, config):  # noqa: ARG002 — 서명만 맞춘다
        self.calls += 1
        if self.calls <= self.fails:
            raise RuntimeError("일시적 API 오류")
        return _FakeResponse(len(contents))


def test_retry_succeeds_after_transient_failures(tmp_path: Path, monkeypatch) -> None:
    """몇 번 실패해도 재시도해서 성공하면 벡터를 돌려준다 (기다림은 건너뜀)."""
    monkeypatch.setattr(gemini_module.time, "sleep", lambda _s: None)
    provider = GeminiEmbeddingProvider(CONFIG, api_key="fake-key", cache=EmbeddingCache(tmp_path))
    provider._client = _FlakyGeminiClient(fails=MAX_RETRIES - 1)  # 마지막 시도에 성공

    result = provider.embed(["기사"])

    assert result.shape == (1, 4)
    assert provider._client.calls == MAX_RETRIES


def test_retry_gives_up_after_max_and_raises(tmp_path: Path, monkeypatch) -> None:
    """정해진 횟수를 넘겨 계속 실패하면 명확한 오류를 낸다."""
    monkeypatch.setattr(gemini_module.time, "sleep", lambda _s: None)
    provider = GeminiEmbeddingProvider(CONFIG, api_key="fake-key", cache=EmbeddingCache(tmp_path))
    provider._client = _FlakyGeminiClient(fails=MAX_RETRIES + 5)  # 끝까지 실패

    with pytest.raises(RuntimeError, match="재시도 실패"):
        provider.embed(["기사"])
    assert provider._client.calls == MAX_RETRIES  # 딱 정해진 횟수만 시도
