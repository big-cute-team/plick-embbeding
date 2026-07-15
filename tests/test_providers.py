"""providers 테스트 — 캐시·정규화. 네트워크 없이 동작해야 한다."""

from pathlib import Path

import numpy as np

from plick_embedding.providers.base import EmbeddingConfig, l2_normalize
from plick_embedding.providers.cache import EmbeddingCache
from plick_embedding.providers.gemini import GeminiEmbeddingProvider
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
