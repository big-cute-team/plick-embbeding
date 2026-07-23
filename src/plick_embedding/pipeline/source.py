"""Supabase article_summaries 증분 로더 — 커서 이후 발행된 PUBLISHED 기사만 가져온다.

기존 `scripts/fetch_articles.py`는 스냅샷 고정용(덮어쓰기 거부)이라, 운영처럼
"마지막으로 처리한 이후 발행된 기사만" 반복해서 가져오는 함수가 없었다. 여기서는
커서(마지막 처리 지점 published_at) 이후에 발행된 PUBLISHED 기사만 Article로 돌려준다.
같은 시각·커서 이전은 제외한다(gt). 이미 처리한 id 건너뛰기는 저장소 몫(T03).

HTTP 호출은 ``fetch`` 콜러블로 주입할 수 있어(기본은 urllib), 테스트에서 외부 API
없이 응답을 모킹한다.
"""

import json
import urllib.parse
import urllib.request
from collections.abc import Callable
from datetime import datetime

from plick_embedding.pipeline.articles import Article

# (url, headers) -> Supabase가 준 행 목록(dict)
JsonFetcher = Callable[[str, dict[str, str]], list[dict]]

_SELECT = "article_summary_id,title,summary_short,published_at"


def build_query(since: datetime, until: datetime | None, limit: int) -> str:
    """PostgREST 질의 문자열 — PUBLISHED · published_at > since (· < until) · 발행순."""
    filters = [f"published_at.gt.{since.isoformat()}"]
    if until is not None:
        filters.append(f"published_at.lt.{until.isoformat()}")
    return urllib.parse.urlencode(
        {
            "select": _SELECT,
            "status": "eq.PUBLISHED",
            "and": f"({','.join(filters)})",
            "order": "published_at.asc",
            "limit": str(limit),
        }
    )


def rows_to_articles(rows: list[dict]) -> list[Article]:
    """Supabase 행 → Article(id·title·summary_short·published_at)."""
    return [
        Article(
            id=str(row["article_summary_id"]),
            title=row["title"],
            summary=row.get("summary_short") or "",
            published_at=datetime.fromisoformat(row["published_at"]),
        )
        for row in rows
    ]


def _urllib_get_json(url: str, headers: dict[str, str]) -> list[dict]:
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request) as response:  # noqa: S310 (신뢰된 Supabase URL)
        return json.loads(response.read().decode("utf-8"))


def fetch_new_articles(
    base_url: str,
    service_key: str,
    since: datetime,
    until: datetime | None = None,
    limit: int = 1000,
    fetch: JsonFetcher = _urllib_get_json,
) -> list[Article]:
    """커서(since) 이후 발행된 PUBLISHED 기사만 발행 시각 순으로 반환한다.

    ``since``는 마지막으로 처리한 기사의 published_at. 그와 **같은 시각은 제외**(gt)하고
    더 뒤에 발행된 것만 가져온다. 서버 질의(gt)로 한 번 거르고, 받은 뒤에도 한 번 더
    확인해(``> since``) 경계가 새면 클라이언트에서 떨군다. 이미 처리한 id 건너뛰기는
    저장소가 맡는다(T03).
    """
    query = build_query(since, until, limit)
    url = f"{base_url.rstrip('/')}/article_summaries?{query}"
    headers = {"apikey": service_key, "Authorization": f"Bearer {service_key}"}
    rows = fetch(url, headers)
    articles = [a for a in rows_to_articles(rows) if a.published_at > since]
    return sorted(articles, key=lambda a: a.published_at)
