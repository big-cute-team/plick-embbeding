"""병합형 군집화 — cosine 유사도, average linkage.

비슷한 것끼리 차례로 합쳐가다가, 군집 간 평균 유사도가 임계값 아래로
떨어지면 멈춘다. 결정적(랜덤성 없음)이라 시드 고정이 필요 없다.
"""

import numpy as np
from sklearn.cluster import AgglomerativeClustering


def cluster_embeddings(embeddings: np.ndarray, threshold: float) -> np.ndarray:
    """(N, dim) 벡터를 묶어 군집 라벨 (N,)을 반환한다.

    threshold는 코사인 "유사도" 기준(예: 0.85) — 내부적으로는
    거리(1 - 유사도)로 바꿔 AgglomerativeClustering에 넘긴다.
    """
    if len(embeddings) == 0:
        return np.array([], dtype=int)
    if len(embeddings) == 1:
        return np.array([0], dtype=int)

    model = AgglomerativeClustering(
        n_clusters=None,
        metric="cosine",
        linkage="average",
        distance_threshold=1.0 - threshold,
    )
    return model.fit_predict(embeddings)
