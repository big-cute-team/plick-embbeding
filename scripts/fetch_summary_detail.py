"""상세요약 보강 스냅샷 (KAN-186 선행) — 고정된 data/articles.json의 같은 90건에
Supabase article_summaries의 summary_detail만 채워 data/articles_detail.json으로 낸다.

원본 스냅샷(articles.json)은 건드리지 않고 title·summary_short·published_at·순서를
그대로 두므로 정답 라벨(articles90.json)이 그대로 유효하다. 상세요약 축(제목+상세요약)
실험은 이 파일을 --input으로 쓴다.

예: uv run python scripts/fetch_summary_detail.py
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
        prog="fetch_summary_detail",
        description="같은 90건에 summary_detail을 채운 스냅샷 생성 (KAN-186 선행)",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=PROJECT_ROOT / "data" / "articles.json",
        help="원본 스냅샷 (기본: data/articles.json)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "data" / "articles_detail.json",
        help="출력 경로 (기본: data/articles_detail.json)",
    )
    return parser


def fetch_details(base_url: str, service_key: str, ids: list[str]) -> dict[str, str]:
    """article_summary_id 목록으로 summary_detail을 조회해 id→상세요약 맵을 만든다."""
    id_list = ",".join(ids)
    query = urllib.parse.urlencode(
        {
            "select": "article_summary_id,summary_detail",
            "article_summary_id": f"in.({id_list})",
            "limit": str(len(ids)),
        }
    )
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/article_summaries?{query}",
        headers={"apikey": service_key, "Authorization": f"Bearer {service_key}"},
    )
    with urllib.request.urlopen(request) as response:
        rows = json.loads(response.read().decode("utf-8"))
    return {str(row["article_summary_id"]): (row.get("summary_detail") or "") for row in rows}


def main() -> None:
    args = build_parser().parse_args()
    if args.output.exists():
        sys.exit(
            f"스냅샷이 이미 있습니다: {args.output}\n"
            "데이터셋은 고정되어야 합니다. 새로 뽑으려면 기존 파일을 지우거나 --output을 바꾸세요."
        )
    if not args.input.exists():
        sys.exit(f"원본 스냅샷이 없습니다: {args.input}")

    load_dotenv(PROJECT_ROOT / ".env.local")
    base_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not base_url or not service_key:
        sys.exit("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY가 없습니다 (.env.local 확인).")

    articles = json.loads(args.input.read_text(encoding="utf-8"))
    ids = [str(a["id"]) for a in articles]
    detail_by_id = fetch_details(base_url, service_key, ids)

    missing = [i for i in ids if not detail_by_id.get(i)]
    if missing:
        sys.exit(
            f"summary_detail이 비어있는 기사 {len(missing)}건 (예: {', '.join(missing[:5])}). "
            "상세요약 축을 돌리려면 모두 채워져 있어야 합니다."
        )

    enriched = [{**a, "summary_detail": detail_by_id[str(a["id"])]} for a in articles]
    args.output.write_text(
        json.dumps(enriched, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lengths = [len(a["summary_detail"]) for a in enriched]
    avg = sum(lengths) // len(lengths)
    print(f"상세요약 보강 완료: {len(enriched)}건 → {args.output}")
    print(f"summary_detail 길이(글자): 최소 {min(lengths)} · 평균 {avg} · 최대 {max(lengths)}")


if __name__ == "__main__":
    main()
