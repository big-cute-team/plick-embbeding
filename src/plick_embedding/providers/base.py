"""임베딩 공급자 공통 인터페이스 — Gemini·OpenAI를 같은 모양으로 감싼다."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class EmbeddingConfig:
    """실험 1회의 임베딩 조건. 캐시 키와 리포트 기록에 그대로 쓰인다."""

    model: str
    task_type: str
    dim: int


class EmbeddingProvider(ABC):
    """텍스트 목록 → (N, dim) 벡터 행렬. 구현체는 캐시를 먼저 확인해야 한다."""

    def __init__(self, config: EmbeddingConfig) -> None:
        self.config = config

    @abstractmethod
    def embed(self, texts: list[str]) -> np.ndarray:
        """L2 정규화된 (len(texts), dim) float32 행렬을 반환한다."""


def l2_normalize(vectors: np.ndarray) -> np.ndarray:
    """행 단위 L2 정규화 — 벡터 길이를 1로 맞춘다 (영벡터는 그대로 둔다)."""
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return (vectors / norms).astype(np.float32)
