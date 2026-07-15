"""기사 스냅샷 로드 — data/의 JSON 파일을 읽어 Article 목록으로 만든다.

기대 형식: [{"id": ..., "title": ..., "summary_short": ..., "published_at": ISO8601}, ...]
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class Article:
    id: str
    title: str
    summary: str
    published_at: datetime
    summary_detail: str = ""  # 상세요약 (있는 스냅샷에서만 채워짐)

    @property
    def embed_text(self) -> str:
        """임베딩 입력 텍스트 — PoC와 동일하게 제목 + 짧은 요약."""
        return f"{self.title}\n{self.summary}"


# 임베딩에 넣는 입력 텍스트 구성 (Phase 05 비교 축).
EMBED_TEXT_MODES = {
    "title": lambda a: a.title,  # 제목만
    "title_short": lambda a: f"{a.title}\n{a.summary}",  # 제목 + 짧은요약 (기본)
    "title_detail": lambda a: f"{a.title}\n{a.summary_detail}",  # 제목 + 상세요약
}


def embed_texts(articles: list["Article"], mode: str = "title_short") -> list[str]:
    """입력 구성 모드에 맞춰 각 기사의 임베딩 입력 텍스트 목록을 만든다."""
    if mode not in EMBED_TEXT_MODES:
        raise ValueError(f"모르는 입력 구성 모드: {mode!r} (가능: {sorted(EMBED_TEXT_MODES)})")
    if mode == "title_detail" and any(not a.summary_detail for a in articles):
        raise ValueError(
            "title_detail 모드인데 summary_detail이 빈 기사가 있습니다 — "
            "상세요약 스냅샷(fetch_summary_detail.py)을 --input으로 쓰세요."
        )
    build = EMBED_TEXT_MODES[mode]
    return [build(a) for a in articles]


def load_articles(path: Path) -> list[Article]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    articles = [
        Article(
            id=str(row["id"]),
            title=row["title"],
            summary=row.get("summary_short") or row.get("summary") or "",
            published_at=datetime.fromisoformat(row["published_at"]),
            summary_detail=row.get("summary_detail") or "",
        )
        for row in rows
    ]
    return sorted(articles, key=lambda a: a.published_at)
