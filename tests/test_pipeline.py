"""pipeline 테스트 — 군집화·시간 범위로 나누기. 네트워크 없이 동작해야 한다."""

from datetime import datetime, timedelta

import numpy as np

from plick_embedding.pipeline.clustering import cluster_embeddings
from plick_embedding.pipeline.window import split_clusters_by_window


def _unit(vector: list[float]) -> list[float]:
    array = np.array(vector)
    return list(array / np.linalg.norm(array))


def test_cluster_similar_vectors_together() -> None:
    embeddings = np.array(
        [
            _unit([1.0, 0.0, 0.01]),
            _unit([1.0, 0.0, 0.02]),  # 위와 거의 같음 → 같은 군집
            _unit([0.0, 1.0, 0.0]),  # 직교 → 다른 군집
        ]
    )
    labels = cluster_embeddings(embeddings, threshold=0.85)

    assert labels[0] == labels[1]
    assert labels[0] != labels[2]
    assert len(set(labels)) == 2


def test_cluster_edge_cases() -> None:
    assert len(cluster_embeddings(np.zeros((0, 3)), threshold=0.85)) == 0
    assert list(cluster_embeddings(np.ones((1, 3)), threshold=0.85)) == [0]


def test_window_splits_stale_cluster() -> None:
    """같은 군집이라도 24h 넘게 잠잠하면 새 이슈로 갈라진다 (사가 분할)."""
    base = datetime(2026, 6, 29, 12, 0)
    published_at = [
        base,
        base + timedelta(hours=3),  # 3h 간격 → 유지
        base + timedelta(hours=40),  # 37h 공백 → 분리
    ]
    labels = np.array([0, 0, 0])

    new_labels = split_clusters_by_window(labels, published_at, timedelta(hours=24))

    assert new_labels[0] == new_labels[1]
    assert new_labels[2] != new_labels[0]


def test_window_keeps_rolling_chain() -> None:
    """이웃 간격이 비교 시간 범위 안이면 전체 길이가 24h를 넘어도 한 이슈다 (이웃 간격 기준)."""
    base = datetime(2026, 6, 29, 12, 0)
    published_at = [base + timedelta(hours=20 * i) for i in range(3)]  # 총 40h
    labels = np.array([0, 0, 0])

    new_labels = split_clusters_by_window(labels, published_at, timedelta(hours=24))

    assert len(set(new_labels)) == 1


def test_window_does_not_merge_different_clusters() -> None:
    base = datetime(2026, 6, 29, 12, 0)
    published_at = [base, base + timedelta(hours=1)]
    labels = np.array([0, 1])

    new_labels = split_clusters_by_window(labels, published_at, timedelta(hours=24))

    assert new_labels[0] != new_labels[1]
