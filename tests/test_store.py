"""벡터 저장소 넣고 빼기 검증 — 파일에 쓰고 다시 읽어도 그대로인지 확인한다."""

from datetime import UTC, datetime, timedelta

import numpy as np
import pytest

from plick_embedding.pipeline import store as store_module
from plick_embedding.pipeline.store import StoredArticle, VectorStore

BASE = datetime(2026, 7, 11, 9, 0, 0, tzinfo=UTC)


def make(article_id: str, hours: float, issue_id: str | None = None) -> StoredArticle:
    return StoredArticle(
        id=article_id,
        published_at=BASE + timedelta(hours=hours),
        vector=np.array([0.6, 0.8], dtype=np.float32),
        model="gemini-embedding-001",
        task_type="SEMANTIC_SIMILARITY",
        dim=768,
        normalized=True,
        issue_id=issue_id,
    )


def test_roundtrip_preserves_vector_and_meta(tmp_path):
    """저장했다 새 저장소로 다시 읽어도 벡터·메타가 같다."""
    path = tmp_path / "vectors.jsonl"
    VectorStore(path).add([make("1", 0), make("2", 1)])

    reloaded = VectorStore(path)
    assert reloaded.known_ids() == {"1", "2"}
    record = reloaded.all()[0]
    assert record.id == "1"
    assert np.allclose(record.vector, [0.6, 0.8])
    assert (record.model, record.task_type, record.dim, record.normalized) == (
        "gemini-embedding-001",
        "SEMANTIC_SIMILARITY",
        768,
        True,
    )


def test_all_sorted_by_published_at(tmp_path):
    """all()은 발행 시각 순으로 돌려준다 (입력이 뒤섞여도)."""
    path = tmp_path / "vectors.jsonl"
    VectorStore(path).add([make("late", 5), make("early", 1), make("mid", 3)])
    assert [r.id for r in VectorStore(path).all()] == ["early", "mid", "late"]


def test_add_ignores_existing_id(tmp_path):
    """이미 있는 id는 덮어쓰지 않는다."""
    path = tmp_path / "vectors.jsonl"
    store = VectorStore(path)
    store.add([make("1", 0, issue_id="keep")])
    store.add([make("1", 0, issue_id="overwrite?")])
    assert store.all()[0].issue_id == "keep"
    assert len(store.known_ids()) == 1


def test_set_issues_persists(tmp_path):
    """묶기 결과(issue_id)를 적으면 다시 읽어도 남아 있다."""
    path = tmp_path / "vectors.jsonl"
    store = VectorStore(path)
    store.add([make("1", 0), make("2", 1)])
    store.set_issues({"1": "issue_0", "2": "issue_0"})

    reloaded = VectorStore(path)
    assert {r.id: r.issue_id for r in reloaded.all()} == {"1": "issue_0", "2": "issue_0"}


def test_save_is_atomic_old_file_survives_failed_write(tmp_path, monkeypatch):
    """저장(바꿔치기)이 도중 실패해도 이전 저장 파일은 온전하다."""
    path = tmp_path / "vectors.jsonl"
    store = VectorStore(path)
    store.add([make("1", 0, issue_id="issue_0")])
    old = path.read_text(encoding="utf-8")

    def boom(*_args):
        raise OSError("바꿔치기 도중 끊김")

    monkeypatch.setattr(store_module.os, "replace", boom)
    with pytest.raises(OSError, match="끊김"):
        store.set_issues({"1": "issue_9"})

    assert path.read_text(encoding="utf-8") == old  # 이전 저장 그대로
