"""eval 테스트 — 라벨 로드·채점. 네트워크 없이 동작해야 한다."""

import json
from datetime import datetime

import numpy as np

from plick_embedding.eval.labels import LabelSet, load_labels
from plick_embedding.eval.scoring import score
from plick_embedding.pipeline.articles import Article


def _article(article_id: str) -> Article:
    return Article(
        id=article_id,
        title=f"제목 {article_id}",
        summary="",
        published_at=datetime(2026, 7, 9, 12, 0),
    )


def _labelset(mapping: dict[str, str]) -> LabelSet:
    return LabelSet(issue_by_article=dict(mapping))


def test_load_labels_normalizes_and_missing(tmp_path) -> None:
    path = tmp_path / "labels.json"
    path.write_text(json.dumps({6894: "santos", "6913": "santos"}), encoding="utf-8")
    labels = load_labels(path)

    assert labels.issue_of("6894") == "santos"  # 숫자 키도 문자열로
    assert labels.n_issues == 1
    assert labels.missing(["6894", "9999"]) == ["9999"]


def test_load_labels_rejects_empty_issue(tmp_path) -> None:
    path = tmp_path / "labels.json"
    path.write_text(json.dumps({"6894": "  "}), encoding="utf-8")
    try:
        load_labels(path)
    except ValueError:
        return
    raise AssertionError("빈 이슈 id는 거부해야 한다")


def test_score_perfect_match() -> None:
    articles = [_article(i) for i in ["a", "b", "c", "d"]]
    labels = _labelset({"a": "x", "b": "x", "c": "y", "d": "y"})
    pred = np.array([0, 0, 1, 1])

    result = score(articles, pred, labels)

    assert result.ari == 1.0
    assert result.pairwise.precision == 1.0
    assert result.pairwise.recall == 1.0
    assert result.pairwise.f1 == 1.0
    assert result.overmerges == []
    assert result.oversplits == []


def test_score_detects_overmerge() -> None:
    """서로 다른 이슈 x·y를 한 묶음으로 합치면 잘못 합침으로 잡힌다."""
    articles = [_article(i) for i in ["a", "b", "c"]]
    labels = _labelset({"a": "x", "b": "y", "c": "y"})
    pred = np.array([0, 0, 0])  # 셋 다 한 묶음

    result = score(articles, pred, labels)

    assert len(result.overmerges) == 1
    case = result.overmerges[0]
    assert set(case.members_by_issue) == {"x", "y"}
    assert result.pairwise.recall == 1.0  # 같은 이슈 쌍은 다 맞음
    assert result.pairwise.precision < 1.0  # 다른 이슈를 합침 → 오탐


def test_score_detects_oversplit() -> None:
    """한 이슈 x를 두 묶음으로 쪼개면 잘못 나뉨으로 잡힌다."""
    articles = [_article(i) for i in ["a", "b", "c"]]
    labels = _labelset({"a": "x", "b": "x", "c": "x"})
    pred = np.array([0, 0, 1])

    result = score(articles, pred, labels)

    assert len(result.oversplits) == 1
    assert result.oversplits[0].issue == "x"
    assert len(result.oversplits[0].members_by_cluster) == 2
    assert result.pairwise.precision == 1.0  # 잘못 합친 건 없음
    assert result.pairwise.recall < 1.0  # 같은 이슈 쌍을 놓침


def test_score_excludes_unlabeled() -> None:
    articles = [_article(i) for i in ["a", "b", "z"]]
    labels = _labelset({"a": "x", "b": "x"})  # z는 정답 없음
    pred = np.array([0, 0, 1])

    result = score(articles, pred, labels)

    assert result.n_labeled == 2
    assert result.n_unlabeled == 1


def test_score_is_deterministic() -> None:
    articles = [_article(i) for i in ["a", "b", "c", "d"]]
    labels = _labelset({"a": "x", "b": "y", "c": "y", "d": "z"})
    pred = np.array([0, 0, 1, 1])

    first = score(articles, pred, labels)
    second = score(articles, pred, labels)

    assert first == second
