"""24h 롤링 윈도우 — 시간상 멀리 떨어진 기사가 한 이슈로 묶이지 않게 한다.

SPEC 정의: 새 글은 발행시각 T 기준 [T-24h, T]에 갱신된 활성 이슈하고만
비교하고, 24h 넘게 잠잠하다 재등장하면 새 이슈다.

전역 군집화 결과에 이 규칙을 적용하기 위해, 각 군집을 발행시각 순으로
정렬한 뒤 이웃 간 간격이 윈도우를 넘는 지점에서 군집을 쪼갠다.
(정확한 PoC 방식은 T05 재현 실험에서 검증 — docs/DECISIONS.md 참조)
"""

from datetime import datetime, timedelta

import numpy as np


def split_clusters_by_window(
    labels: np.ndarray,
    published_at: list[datetime],
    window: timedelta,
) -> np.ndarray:
    """군집 라벨 (N,)에 윈도우 분리를 적용한 새 라벨 (N,)을 반환한다."""
    if len(labels) == 0:
        return labels

    new_labels = np.full(len(labels), -1, dtype=int)
    next_label = 0
    for label in np.unique(labels):
        indices = np.where(labels == label)[0]
        indices = indices[np.argsort([published_at[i] for i in indices])]

        current = [indices[0]]
        groups = [current]
        for prev, cur in zip(indices[:-1], indices[1:], strict=True):
            if published_at[cur] - published_at[prev] > window:
                current = []
                groups.append(current)
            current.append(cur)

        for group in groups:
            new_labels[group] = next_label
            next_label += 1

    return new_labels
