"""전체 처리 흐름 검증 — 인터넷(외부 API) 없이 가짜 벡터로 결정적으로 확인한다.

핵심: 두 번 연속 돌리면 2회차는 새 기사만(=0건) 처리하고, 묶음 결과가 같다.
"""

from datetime import UTC, datetime, timedelta

import numpy as np
import pytest

from plick_embedding.pipeline.articles import Article, embed_texts
from plick_embedding.pipeline.batch import run_pipeline
from plick_embedding.pipeline.store import VectorStore
from plick_embedding.providers.base import EmbeddingConfig, EmbeddingProvider

BASE = datetime(2026, 7, 11, 9, 0, 0, tzinfo=UTC)
CONFIG = EmbeddingConfig(model="gemini-embedding-001", task_type="SEMANTIC_SIMILARITY", dim=2)
WINDOW = timedelta(hours=24)


def unit(x: float, y: float) -> np.ndarray:
    v = np.array([x, y], dtype=np.float32)
    return v / np.linalg.norm(v)


def article(article_id: str, hours: float, title: str, summary: str) -> Article:
    return Article(
        id=article_id, title=title, summary=summary, published_at=BASE + timedelta(hours=hours)
    )


class StubProvider(EmbeddingProvider):
    """API 없이, 미리 정한 벡터를 돌려주고 몇 건을 임베딩했는지 센다."""

    def __init__(self, config: EmbeddingConfig, by_text: dict[str, np.ndarray]) -> None:
        super().__init__(config)
        self.by_text = by_text
        self.embedded: list[str] = []

    def embed(self, texts: list[str]) -> np.ndarray:
        self.embedded.extend(texts)
        return np.vstack([self.by_text[t] for t in texts])


# 두 기사는 같은 방향(같은 이슈), 하나는 직각(딴 이슈)
ARTICLES = [
    article("1", 0, "이적A", "협상 시작"),
    article("2", 1, "이적A 후속", "메디컬 진행"),
    article("3", 2, "다른뉴스", "경기 결과"),
]
VECTORS = {
    embed_texts([ARTICLES[0]])[0]: unit(1, 0),
    embed_texts([ARTICLES[1]])[0]: unit(1, 0),
    embed_texts([ARTICLES[2]])[0]: unit(0, 1),
}


def test_first_run_processes_all_and_writes_issues(tmp_path):
    """1회차: 전부 새로 처리, 벡터·메타·이슈가 저장된다."""
    store = VectorStore(tmp_path / "vectors.jsonl")
    provider = StubProvider(CONFIG, VECTORS)
    result = run_pipeline(ARTICLES, provider, store, threshold=0.86, window=WINDOW)

    assert result.new_count == 3
    assert len(provider.embedded) == 3
    assert result.total == 3
    assert result.issue_count == 2  # 1·2 한 이슈, 3 딴 이슈

    reloaded = {r.id: r for r in VectorStore(tmp_path / "vectors.jsonl").all()}
    assert reloaded["1"].issue_id == reloaded["2"].issue_id
    assert reloaded["1"].issue_id != reloaded["3"].issue_id
    assert reloaded["1"].normalized is True
    assert reloaded["1"].model == "gemini-embedding-001"


def test_second_run_processes_nothing_and_same_result(tmp_path):
    """2회차: 같은 입력이면 새로 처리 0건, 묶음 결과가 그대로다."""
    path = tmp_path / "vectors.jsonl"
    run_pipeline(
        ARTICLES, StubProvider(CONFIG, VECTORS), VectorStore(path), threshold=0.86, window=WINDOW
    )
    first = {r.id: r.issue_id for r in VectorStore(path).all()}

    provider2 = StubProvider(CONFIG, VECTORS)
    result2 = run_pipeline(ARTICLES, provider2, VectorStore(path), threshold=0.86, window=WINDOW)

    assert result2.new_count == 0
    assert provider2.embedded == []  # 다시 임베딩하지 않는다
    assert {r.id: r.issue_id for r in VectorStore(path).all()} == first


def test_third_article_added_later_only_it_is_processed(tmp_path):
    """1·2만 처리한 뒤 3이 새로 오면 3만 새로 처리한다(이어서)."""
    path = tmp_path / "vectors.jsonl"
    run_pipeline(
        ARTICLES[:2],
        StubProvider(CONFIG, VECTORS),
        VectorStore(path),
        threshold=0.86,
        window=WINDOW,
    )

    provider = StubProvider(CONFIG, VECTORS)
    result = run_pipeline(ARTICLES, provider, VectorStore(path), threshold=0.86, window=WINDOW)

    assert result.new_count == 1
    assert provider.embedded == [embed_texts([ARTICLES[2]])[0]]
    assert result.total == 3


class CrashingProvider(EmbeddingProvider):
    """임베딩 도중 끊긴 상황을 흉내 — embed에서 바로 터진다."""

    def embed(self, texts: list[str]) -> np.ndarray:
        raise RuntimeError("임베딩 도중 끊김")


def test_pipeline_resumes_after_crash_without_duplicate(tmp_path):
    """중간에 끊긴 뒤 다시 돌리면 반쪽 저장 없이 중복 없이 끝낸다."""
    path = tmp_path / "vectors.jsonl"

    with pytest.raises(RuntimeError, match="끊김"):
        run_pipeline(
            ARTICLES, CrashingProvider(CONFIG), VectorStore(path), threshold=0.86, window=WINDOW
        )
    assert VectorStore(path).known_ids() == set()  # 반쪽 저장이 남지 않음

    provider = StubProvider(CONFIG, VECTORS)
    result = run_pipeline(ARTICLES, provider, VectorStore(path), threshold=0.86, window=WINDOW)

    assert result.new_count == 3
    assert result.total == 3
    assert len(provider.embedded) == 3  # 각 기사 딱 한 번만 임베딩
    assert len(VectorStore(path).known_ids()) == 3  # 중복 없음
