"""하나씩 묶기 — 기사를 발행 시각 순으로 한 건씩 처리해 묶는다.

배치(`cluster_embeddings`)는 전체를 한 번에 보지만, 운영은 새 기사가 하나씩
들어온다. 여기서는 발행 시각이 이른 기사부터 한 건씩 보며:

1. 최근 N시간 안에 살아 있는 묶음(마지막 갱신이 window 안)만 후보로 추린다.
2. 후보들의 대표값과 코사인 유사도(정규화 벡터라 내적)를 재 가장 비슷한 걸 찾는다.
3. 가장 비슷한 값이 기준값 이상이면 그 묶음에 넣고 묶음의 갱신 시각을 이 기사의
   발행 시각으로 새로 찍는다(= 새 글이 붙을 때마다 수명 갱신). 아니면 새 묶음.

랜덤성이 없어 결정적이다. 반환 라벨은 **입력 순서에 맞춰** 정렬되므로 채점기·
리포트에 그대로 넘길 수 있다(발행 시각으로 다시 정렬하지 않아도 된다).

대표값(representative)은 3가지 — 뒤 실험(대표값 비교)에서 나란히 채점한다:
- ``centroid``: 소속 기사 벡터들의 평균을 다시 정규화한 값 (기본)
- ``latest``: 가장 최근에 붙은 기사의 벡터
- ``seed``: 묶음을 처음 시작한 기사의 벡터 (안 바뀜)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta

import numpy as np

REPRESENTATIVES = ("centroid", "latest", "seed")


@dataclass
class _Cluster:
    label: int
    representative: str
    rep: np.ndarray  # 비교에 쓰는 대표 벡터 (정규화됨)
    updated: datetime  # 마지막으로 기사가 붙은 시각
    _sum: np.ndarray = field(repr=False)  # centroid용 누적 합
    _count: int = 1

    def add(self, vec: np.ndarray, when: datetime) -> None:
        self._count += 1
        self._sum = self._sum + vec
        self.updated = when
        if self.representative == "centroid":
            centroid = self._sum / self._count
            norm = float(np.linalg.norm(centroid))
            self.rep = centroid / norm if norm else centroid
        elif self.representative == "latest":
            self.rep = vec
        # seed: 대표값을 바꾸지 않는다


def cluster_incrementally(
    embeddings: np.ndarray,
    published_at: list[datetime],
    threshold: float,
    window: timedelta,
    representative: str = "centroid",
) -> np.ndarray:
    """(N, dim) 벡터를 발행 시각 순으로 하나씩 묶어 라벨 (N,)을 반환한다.

    embeddings는 L2 정규화돼 있다고 본다(공급자 규약). threshold는 코사인
    "유사도" 기준(예: 0.86), window는 살아 있는 묶음으로 볼 시간 범위.
    라벨은 입력과 같은 순서로 반환한다.
    """
    if representative not in REPRESENTATIVES:
        raise ValueError(f"모르는 대표값: {representative!r} (가능: {REPRESENTATIVES})")
    if len(embeddings) != len(published_at):
        raise ValueError("embeddings와 published_at 길이가 다릅니다.")
    n = len(embeddings)
    if n == 0:
        return np.array([], dtype=int)

    # 발행 시각이 이른 것부터 처리하되, 같은 시각은 입력 순서를 지킨다(결정적).
    order = sorted(range(n), key=lambda i: published_at[i])

    labels = np.full(n, -1, dtype=int)
    clusters: list[_Cluster] = []
    for i in order:
        vec = embeddings[i]
        when = published_at[i]

        best: _Cluster | None = None
        best_sim = -1.0
        for cluster in clusters:
            if when - cluster.updated > window:
                continue  # 24시간 넘게 잠잠한 묶음은 후보에서 뺀다
            sim = float(np.dot(vec, cluster.rep))
            if sim > best_sim:
                best, best_sim = cluster, sim

        if best is not None and best_sim >= threshold:
            best.add(vec, when)
            labels[i] = best.label
        else:
            cluster = _Cluster(
                label=len(clusters),
                representative=representative,
                rep=vec,
                updated=when,
                _sum=vec.copy(),
            )
            clusters.append(cluster)
            labels[i] = cluster.label

    return labels
