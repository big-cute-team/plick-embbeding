"""파티션 군집화(KAN-273) 테스트 — 다른 파티션은 절대 안 묶인다."""

import numpy as np
import pytest

from plick_embedding.pipeline.clustering import cluster_within_partitions


def test_different_partitions_never_merge() -> None:
    # 벡터 4개가 모두 거의 동일(전역이면 한 묶음)하지만 파티션이 둘로 갈린다.
    embeddings = np.array(
        [[1.0, 0.0], [0.999, 0.001], [1.0, 0.0], [0.999, 0.001]], dtype=np.float32
    )
    partition = ["A", "A", "B", "B"]
    labels = cluster_within_partitions(embeddings, partition, threshold=0.85)

    # A끼리, B끼리만 같은 라벨. A와 B는 절대 안 겹친다.
    assert labels[0] == labels[1]
    assert labels[2] == labels[3]
    assert set(labels[:2]).isdisjoint(set(labels[2:]))


def test_within_partition_respects_threshold() -> None:
    # 같은 파티션이라도 유사도가 기준 미달이면 안 묶인다.
    embeddings = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    labels = cluster_within_partitions(embeddings, ["A", "A"], threshold=0.85)
    assert labels[0] != labels[1]


def test_length_mismatch_raises() -> None:
    with pytest.raises(ValueError):
        cluster_within_partitions(np.ones((3, 2)), ["A", "B"], threshold=0.85)


def test_deterministic() -> None:
    embeddings = np.array([[1.0, 0.0], [0.9, 0.1], [0.0, 1.0]], dtype=np.float32)
    partition = ["A", "A", "B"]
    first = cluster_within_partitions(embeddings, partition, threshold=0.8)
    second = cluster_within_partitions(embeddings, partition, threshold=0.8)
    assert list(first) == list(second)
