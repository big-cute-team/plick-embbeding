"""하나씩 묶기(incremental) 검증 — 합성 벡터로 결정적으로 확인한다.

실제 임베딩 API를 부르지 않는다. 벡터는 손으로 만든 단위 벡터라 유사도(내적)를
정확히 통제할 수 있다.
"""

from datetime import datetime, timedelta

import numpy as np
import pytest

from plick_embedding.pipeline.incremental import cluster_incrementally

WINDOW = timedelta(hours=24)
BASE = datetime(2026, 7, 1, 0, 0, 0)


def unit(x: float, y: float) -> np.ndarray:
    v = np.array([x, y], dtype=np.float32)
    return v / np.linalg.norm(v)


def at(hours: float) -> datetime:
    return BASE + timedelta(hours=hours)


def test_similar_within_window_same_cluster():
    """비슷하고 24시간 안이면 한 묶음."""
    emb = np.vstack([unit(1, 0), unit(1, 0)])
    labels = cluster_incrementally(emb, [at(0), at(1)], threshold=0.86, window=WINDOW)
    assert labels[0] == labels[1]


def test_similar_but_beyond_window_new_cluster():
    """비슷해도 마지막 갱신 뒤 24시간을 넘기면 새 묶음."""
    emb = np.vstack([unit(1, 0), unit(1, 0)])
    labels = cluster_incrementally(emb, [at(0), at(30)], threshold=0.86, window=WINDOW)
    assert labels[0] != labels[1]


def test_dissimilar_within_window_new_cluster():
    """시간 안이어도 안 비슷하면 새 묶음."""
    emb = np.vstack([unit(1, 0), unit(0, 1)])  # 내적 0
    labels = cluster_incrementally(emb, [at(0), at(1)], threshold=0.86, window=WINDOW)
    assert labels[0] != labels[1]


def test_rolling_updates_extend_life_beyond_window():
    """중간에 계속 붙으면 첫 기사에서 24시간을 넘어도 한 묶음으로 이어진다."""
    emb = np.vstack([unit(1, 0), unit(1, 0), unit(1, 0)])
    labels = cluster_incrementally(emb, [at(0), at(20), at(40)], threshold=0.86, window=WINDOW)
    assert labels[0] == labels[1] == labels[2]  # 0→40h(>24h)지만 20h 간격이라 이어짐


def test_labels_align_to_input_order_when_unsorted():
    """입력이 발행 시각 순이 아니어도 라벨은 입력 순서에 맞춰 나온다."""
    # 입력 순서: 늦은 기사가 먼저. 내용은 [1,0]/[0,1]/[1,0]
    emb = np.vstack([unit(1, 0), unit(0, 1), unit(1, 0)])
    published = [at(10), at(11), at(0)]  # index0·2가 같은 내용
    labels = cluster_incrementally(emb, published, threshold=0.86, window=WINDOW)
    assert labels[0] == labels[2]  # 같은 내용·시간 안 → 같은 묶음
    assert labels[1] != labels[0]  # 다른 내용 → 다른 묶음


def test_representative_latest_vs_seed_differ():
    """대표값이 'latest'면 흘러가고 'seed'면 첫 기사에 고정 — 결과가 갈린다.

    seed=[1,0]에 [0.894,0.447]이 붙어 대표가 흘러가면(latest) 다음 [0.196,0.980]이
    붙지만, 대표를 첫 기사로 고정하면(seed) 안 붙는다. (기준값 0.5)
    """
    emb = np.vstack([unit(1, 0), unit(1, 0.5), unit(0.2, 1)])
    times = [at(0), at(1), at(2)]

    latest = cluster_incrementally(
        emb, times, threshold=0.5, window=WINDOW, representative="latest"
    )
    assert latest[0] == latest[1] == latest[2]  # 대표가 흘러가 3번째도 붙음

    seed = cluster_incrementally(emb, times, threshold=0.5, window=WINDOW, representative="seed")
    assert seed[0] == seed[1]  # 2번째는 첫 기사와 충분히 비슷해 붙음
    assert seed[2] != seed[0]  # 3번째는 첫 기사와 안 비슷해 새 묶음


def test_deterministic_same_input_same_labels():
    """같은 입력이면 항상 같은 라벨."""
    emb = np.vstack([unit(1, 0), unit(1, 0), unit(0, 1)])
    times = [at(0), at(1), at(2)]
    a = cluster_incrementally(emb, times, threshold=0.86, window=WINDOW)
    b = cluster_incrementally(emb, times, threshold=0.86, window=WINDOW)
    assert np.array_equal(a, b)


def test_empty_input():
    labels = cluster_incrementally(np.empty((0, 2)), [], threshold=0.86, window=WINDOW)
    assert labels.shape == (0,)


def test_unknown_representative_raises():
    emb = np.vstack([unit(1, 0)])
    with pytest.raises(ValueError, match="모르는 대표값"):
        cluster_incrementally(emb, [at(0)], threshold=0.86, window=WINDOW, representative="mean")


def test_length_mismatch_raises():
    emb = np.vstack([unit(1, 0), unit(0, 1)])
    with pytest.raises(ValueError, match="길이가 다릅니다"):
        cluster_incrementally(emb, [at(0)], threshold=0.86, window=WINDOW)
