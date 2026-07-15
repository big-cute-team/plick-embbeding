"""OpenAI 임베딩 공급자 (text-embedding-3-small / -large).

- 벡터 크기(dimensions)를 옵션으로 받는다. text-embedding-3는 차원 축소를
  지원한다(짧게 자른 뒤에도 의미를 최대한 보존).
- OpenAI에는 용도 설정(task_type) 개념이 없다 — 범용 벡터 하나뿐.
  캐시 키 일관성을 위해 config.task_type은 "none"으로 두고 쓴다.
- 차원을 줄이면 길이가 1이 아닐 수 있어 L2 정규화를 직접 한다.
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


class OpenAIEmbeddingProvider(EmbeddingProvider):
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
            from openai import OpenAI

            self._client = OpenAI(api_key=self._api_key)
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
        client = self._get_client()
        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                response = client.embeddings.create(
                    model=self.config.model, input=texts, dimensions=self.config.dim
                )
                raw = np.array([item.embedding for item in response.data], dtype=np.float32)
                return l2_normalize(raw)
            except Exception as error:  # noqa: BLE001 — SDK 예외 계층이 넓어 전부 재시도
                last_error = error
                if attempt < MAX_RETRIES - 1:
                    time.sleep(BACKOFF_BASE_SECONDS * (2**attempt))
        raise RuntimeError(f"OpenAI 임베딩 {MAX_RETRIES}회 재시도 실패") from last_error
