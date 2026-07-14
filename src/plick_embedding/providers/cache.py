"""임베딩 로컬 캐시 — 같은 (텍스트 × 모델 × task_type × 차원)은 API를 두 번 부르지 않는다.

벡터 1개 = 파일 1개(.npy)라서 배치 도중 실패해도 받은 것까지는 남고,
다음 실행에서 없는 것만 다시 호출한다 (부분 실패 재개).
"""

import hashlib
from pathlib import Path

import numpy as np

from plick_embedding.providers.base import EmbeddingConfig
from plick_embedding.settings import PROJECT_ROOT

DEFAULT_CACHE_DIR = PROJECT_ROOT / ".cache" / "embeddings"


class EmbeddingCache:
    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, text: str, config: EmbeddingConfig) -> Path:
        key = f"{config.model}|{config.task_type}|{config.dim}|{text}"
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{digest}.npy"

    def get(self, text: str, config: EmbeddingConfig) -> np.ndarray | None:
        path = self._path(text, config)
        if not path.exists():
            return None
        return np.load(path)

    def put(self, text: str, config: EmbeddingConfig, vector: np.ndarray) -> None:
        np.save(self._path(text, config), vector.astype(np.float32))
