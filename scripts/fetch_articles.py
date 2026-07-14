"""실험 데이터셋 추출 — Supabase article_summaries에서 published 기사를 뽑아
`data/articles.json`으로 고정한다 (P02-T01).

스냅샷은 한 번 고정하면 다시 바뀌면 안 되므로, 출력 파일이 이미 있으면
거부한다. 갱신이 필요하면 새 파일명을 --output으로 지정할 것.

예: uv run python scripts/fetch_articles.py \\
        --since 2026-07-09T00:00:00Z --until 2026-07-14T00:00:00Z
"""

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

from plick_embedding.settings import PROJECT_ROOT


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fetch_articles",
        description="Supabase article_summaries → data/articles.json 스냅샷 추출",
    )
    parser.add_argument("--since", required=True, help="published_at 시작 (ISO8601, 포함)")
    parser.add_argument("--until", required=True, help="published_at 끝 (ISO8601, 미포함)")
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "data" / "articles.json",
        help="출력 경로 (기본: data/articles.json)",
    )
    return parser


def fetch_published(base_url: str, service_key: str, since: str, until: str) -> list[dict]:
    query = urllib.parse.urlencode(
        {
            "select": "article_summary_id,title,summary_short,published_at",
            "status": "eq.PUBLISHED",
            "and": f"(published_at.gte.{since},published_at.lt.{until})",
            "order": "published_at.asc",
            "limit": "1000",
        }
    )
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/article_summaries?{query}",
        headers={"apikey": service_key, "Authorization": f"Bearer {service_key}"},
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    args = build_parser().parse_args()

    if args.output.exists():
        sys.exit(
            f"스냅샷이 이미 있습니다: {args.output}\n"
            "데이터셋은 고정되어야 합니다. 새 스냅샷이 필요하면 --output으로 "
            "다른 파일명을 지정하세요."
        )

    load_dotenv(PROJECT_ROOT / ".env.local")
    base_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not base_url or not service_key:
        sys.exit("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY가 없습니다 (.env.local 확인).")

    rows = fetch_published(base_url, service_key, args.since, args.until)
    articles = [
        {
            "id": row["article_summary_id"],
            "title": row["title"],
            "summary_short": row["summary_short"],
            "published_at": row["published_at"],
        }
        for row in rows
    ]

    args.output.write_text(
        json.dumps(articles, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"기사 {len(articles)}건 저장: {args.output}")
    print(f"기간: {args.since} ~ {args.until} (published_at, UTC)")


if __name__ == "__main__":
    main()
