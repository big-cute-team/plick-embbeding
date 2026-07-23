"""애매한 구간 LLM 판정 묶기 검증 — 스텁 판정기로 API 없이 결정적으로 확인한다."""

from datetime import datetime, timedelta

import numpy as np

from plick_embedding.judge import JudgeCache, parse_verdict
from plick_embedding.pipeline.gray_zone import cluster_with_gray_zone_judge

WINDOW = timedelta(hours=24)
BASE = datetime(2026, 7, 1)
LO, HI = 0.80, 0.90


def unit(x: float, y: float) -> np.ndarray:
    v = np.array([x, y], dtype=np.float32)
    return v / np.linalg.norm(v)


def at(h: float) -> datetime:
    return BASE + timedelta(hours=h)


def _sim(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))


def test_above_high_auto_joins_without_judge():
    """확실히 비슷하면(>=0.90) LLM 안 부르고 붙인다."""
    emb = np.vstack([unit(1, 0), unit(1, 0)])  # 유사도 1.0
    called = []

    def judge(a, b):
        called.append((a, b))
        return False

    labels, n = cluster_with_gray_zone_judge(
        emb, [at(0), at(1)], ["A", "B"], 0.86, WINDOW, LO, HI, judge
    )
    assert labels[0] == labels[1]  # 붙음
    assert n == 0 and not called  # 판정기 호출 안 함


def test_below_low_auto_new_without_judge():
    """확실히 다르면(<0.80) LLM 안 부르고 새 묶음."""
    emb = np.vstack([unit(1, 0), unit(0, 1)])  # 유사도 0.0
    labels, n = cluster_with_gray_zone_judge(
        emb, [at(0), at(1)], ["A", "B"], 0.86, WINDOW, LO, HI, lambda a, b: True
    )
    assert labels[0] != labels[1]
    assert n == 0


def _gray_pair():
    """유사도가 [0.80, 0.90] 안에 들어오는 두 벡터."""
    a = unit(1, 0)
    b = unit(1, 0.5)  # cos ≈ 0.894
    assert LO <= _sim(a, b) <= HI
    return a, b


def test_gray_zone_judge_yes_joins():
    """애매한 구간에서 판정기가 '예'면 붙는다."""
    a, b = _gray_pair()
    emb = np.vstack([a, b])
    labels, n = cluster_with_gray_zone_judge(
        emb, [at(0), at(1)], ["A", "B"], 0.86, WINDOW, LO, HI, lambda x, y: True
    )
    assert labels[0] == labels[1]
    assert n == 1  # 한 번 물어봄


def test_gray_zone_judge_no_splits():
    """애매한 구간에서 판정기가 '아니오'면 새 묶음 — 유사도만으론 붙였을 것."""
    a, b = _gray_pair()
    emb = np.vstack([a, b])
    labels, n = cluster_with_gray_zone_judge(
        emb, [at(0), at(1)], ["A", "B"], 0.86, WINDOW, LO, HI, lambda x, y: False
    )
    assert labels[0] != labels[1]
    assert n == 1


def test_judge_sees_whole_cluster():
    """판정기 두 번째 인자는 후보 묶음의 첫 기사만이 아니라 소속 기사 전체다."""
    seen = []

    def judge(new_text, cluster_text):
        seen.append((new_text, cluster_text))
        return True

    # A, B는 유사도 1.0이라 자동으로 한 묶음이 되고(판정기 안 부름),
    # C는 애매 구간이라 판정기에 A·B 텍스트가 함께 넘어가야 한다.
    emb = np.vstack([unit(1, 0), unit(1, 0), unit(1, 0.5)])
    cluster_with_gray_zone_judge(
        embeddings=emb,
        published_at=[at(0), at(1), at(2)],
        texts=["기사A", "기사B", "기사C"],
        threshold=0.86,
        window=WINDOW,
        gray_low=LO,
        gray_high=HI,
        judge=judge,
    )
    assert seen == [("기사C", "기사A\n---\n기사B")]


def test_empty_input():
    labels, n = cluster_with_gray_zone_judge(
        np.empty((0, 2)), [], [], 0.86, WINDOW, LO, HI, lambda a, b: True
    )
    assert labels.shape == (0,) and n == 0


def test_parse_verdict():
    assert parse_verdict("예") is True
    assert parse_verdict("예, 같은 사건입니다") is True
    assert parse_verdict("Yes") is True
    assert parse_verdict("아니오") is False
    assert parse_verdict("아니오, 다른 사건") is False
    assert parse_verdict("잘 모르겠음") is False  # 애매하면 보수적으로 False


def test_judge_cache_round_trip(tmp_path):
    cache = JudgeCache(cache_dir=tmp_path)
    assert cache.get("m", "a", "b") is None
    cache.put("m", "a", "b", "예")
    assert cache.get("m", "a", "b") == "예"
    # 다른 순서·다른 모델은 별개 키
    assert cache.get("m", "b", "a") is None
    assert cache.get("m2", "a", "b") is None
