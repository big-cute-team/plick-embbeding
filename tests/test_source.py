"""Supabase 증분 로더 검증 — 외부 API 없이 응답을 모킹해 결정적으로 확인한다.

실제 Supabase를 부르지 않는다. ``fetch`` 콜러블에 캔 응답을 넣어 커서 경계·매핑·
정렬을 통제한다.
"""

from datetime import UTC, datetime, timedelta

from plick_embedding.pipeline.articles import Article
from plick_embedding.pipeline.source import (
    build_query,
    fetch_new_articles,
    rows_to_articles,
)

CURSOR = datetime(2026, 7, 11, 9, 0, 0, tzinfo=UTC)


def iso(dt: datetime) -> str:
    return dt.isoformat()


def row(article_id: int, when: datetime, title: str = "제목", summary: str = "요약") -> dict:
    return {
        "article_summary_id": article_id,
        "title": title,
        "summary_short": summary,
        "published_at": iso(when),
    }


def stub(rows: list[dict]):
    """호출 인자를 기록하고 미리 정한 rows를 돌려주는 fetch 스텁."""
    calls: list[tuple[str, dict]] = []

    def _fetch(url: str, headers: dict[str, str]) -> list[dict]:
        calls.append((url, headers))
        return rows

    _fetch.calls = calls  # type: ignore[attr-defined]
    return _fetch


def test_returns_only_articles_after_cursor():
    """커서보다 뒤에 발행된 기사만 돌려준다 (커서 이전·같은 시각 제외)."""
    rows = [
        row(1, CURSOR - timedelta(hours=1)),  # 이전 — 제외
        row(2, CURSOR),  # 같은 시각 — 제외
        row(3, CURSOR + timedelta(hours=1)),  # 이후 — 포함
        row(4, CURSOR + timedelta(hours=2)),  # 이후 — 포함
    ]
    articles = fetch_new_articles("https://x.supabase.co/rest/v1", "key", CURSOR, fetch=stub(rows))
    assert [a.id for a in articles] == ["3", "4"]
    assert all(isinstance(a, Article) for a in articles)


def test_boundary_same_time_excluded_even_if_server_returns_it():
    """서버가 경계를 새서 커서와 같은 시각을 돌려줘도 클라이언트가 떨군다."""
    articles = fetch_new_articles(
        "https://x.supabase.co/rest/v1", "key", CURSOR, fetch=stub([row(2, CURSOR)])
    )
    assert articles == []


def test_results_sorted_by_published_at():
    """발행 시각 순으로 정렬해 돌려준다 (입력이 뒤섞여도)."""
    rows = [
        row(3, CURSOR + timedelta(hours=3)),
        row(1, CURSOR + timedelta(hours=1)),
        row(2, CURSOR + timedelta(hours=2)),
    ]
    articles = fetch_new_articles("https://x.supabase.co/rest/v1", "key", CURSOR, fetch=stub(rows))
    assert [a.id for a in articles] == ["1", "2", "3"]


def test_rows_mapped_to_article_fields():
    """행이 Article 필드로 바르게 매핑된다."""
    articles = rows_to_articles([row(7, CURSOR, title="첼시 영입", summary="확정")])
    assert articles[0] == Article(id="7", title="첼시 영입", summary="확정", published_at=CURSOR)


def test_build_query_filters_published_and_after_cursor():
    """질의는 PUBLISHED · published_at.gt.<커서>(gte 아님) · 발행 오름차순."""
    query = build_query(CURSOR, until=None, limit=1000)
    assert "status=eq.PUBLISHED" in query
    assert f"published_at.gt.{iso(CURSOR)}" in urllib_unquote(query)
    assert "published_at.gte" not in urllib_unquote(query)
    assert "order=published_at.asc" in query


def test_fetch_called_with_auth_headers_and_url():
    """apikey·Bearer 헤더와 article_summaries 엔드포인트로 부른다."""
    fetch = stub([])
    fetch_new_articles("https://x.supabase.co/rest/v1/", "secret", CURSOR, fetch=fetch)
    url, headers = fetch.calls[0]  # type: ignore[attr-defined]
    assert url.startswith("https://x.supabase.co/rest/v1/article_summaries?")
    assert headers["apikey"] == "secret"
    assert headers["Authorization"] == "Bearer secret"


def urllib_unquote(s: str) -> str:
    from urllib.parse import unquote_plus

    return unquote_plus(s)
