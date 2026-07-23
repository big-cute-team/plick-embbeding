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


def cluster_within_partitions(
    embeddings: np.ndarray, partition: list[str], threshold: float
) -> np.ndarray:
    """파티션(예: 카테고리·주체)이 같은 기사끼리만 군집화한다.

    다른 파티션끼리는 아무리 비슷해도 절대 안 묶인다 — "분야·핵심 대상이 다르면
    안 묶기"(KAN-273)를 임베딩 군집화 위에 얹는 방법. 파티션 안에서만
    `cluster_embeddings`를 돌리고, 라벨이 전역에서 겹치지 않게 이어 붙인다.
    등장 순서로 처리해 결정적이다.
    """
    if len(embeddings) != len(partition):
        raise ValueError("embeddings와 partition 길이가 다릅니다.")
    labels = np.full(len(embeddings), -1, dtype=int)
    next_label = 0
    for key in dict.fromkeys(partition):
        idx = np.array([i for i, p in enumerate(partition) if p == key])
        sub = cluster_embeddings(embeddings[idx], threshold)
        for local_i, global_i in zip(sub, idx, strict=True):
            labels[global_i] = next_label + int(local_i)
        next_label += (int(sub.max()) + 1) if len(sub) else 0
    return labels
