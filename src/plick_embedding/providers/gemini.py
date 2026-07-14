"""Gemini 임베딩 공급자 (gemini-embedding-001).

- task_type과 output_dimensionality(차원)를 옵션으로 받는다.
- 3072차원이 아니면 API가 정규화를 보장하지 않으므로 L2 정규화를 직접 한다.
- 캐시에 있는 텍스트는 API를 부르지 않고, 없는 것만 배치로 호출한다.
- 호출 실패 시 지수 백오프로 재시도한다.
"""

import time

import numpy as np

from plick_embedding.providers.base import EmbeddingConfig, EmbeddingProvider, l2_normalize
from plick_embedding.providers.cache import EmbeddingCache

BATCH_SIZE = 100
MAX_RETRIES = 4
BACKOFF_BASE_SECONDS = 2.0


class GeminiEmbeddingProvider(EmbeddingProvider):
    def __init__(
        self,
        config: EmbeddingConfig,
        api_key: str,
        cache: EmbeddingCache | None = None,
    ) -> None:
        super().__init__(config)
        self._api_key = api_key
        self._cache = cache or EmbeddingCache()
        self._client = None  # 캐시만으로 끝나면 클라이언트를 만들지 않는다

    def _get_client(self):
        if self._client is None:
            from google import genai

            self._client = genai.Client(api_key=self._api_key)
        return self._client

    def embed(self, texts: list[str]) -> np.ndarray:
        vectors: dict[int, np.ndarray] = {}
        missing: list[tuple[int, str]] = []
        for i, text in enumerate(texts):
            cached = self._cache.get(text, self.config)
            if cached is not None:
                vectors[i] = cached
            else:
                missing.append((i, text))

        for start in range(0, len(missing), BATCH_SIZE):
            batch = missing[start : start + BATCH_SIZE]
            fetched = self._embed_batch([text for _, text in batch])
            for (i, text), vector in zip(batch, fetched, strict=True):
                self._cache.put(text, self.config, vector)
                vectors[i] = vector

        return np.vstack([vectors[i] for i in range(len(texts))])

    def _embed_batch(self, texts: list[str]) -> np.ndarray:
        from google.genai import types

        client = self._get_client()
        config = types.EmbedContentConfig(
            task_type=self.config.task_type,
            output_dimensionality=self.config.dim,
        )
        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                response = client.models.embed_content(
                    model=self.config.model, contents=texts, config=config
                )
                raw = np.array([e.values for e in response.embeddings], dtype=np.float32)
                return l2_normalize(raw)
            except Exception as error:  # noqa: BLE001 — SDK 예외 계층이 넓어 전부 재시도
                last_error = error
                if attempt < MAX_RETRIES - 1:
                    time.sleep(BACKOFF_BASE_SECONDS * (2**attempt))
        raise RuntimeError(f"Gemini 임베딩 {MAX_RETRIES}회 재시도 실패") from last_error
