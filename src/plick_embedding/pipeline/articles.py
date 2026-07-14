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

    @property
    def embed_text(self) -> str:
        """임베딩 입력 텍스트 — PoC와 동일하게 제목 + 짧은 요약."""
        return f"{self.title}\n{self.summary}"


def load_articles(path: Path) -> list[Article]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    articles = [
        Article(
            id=str(row["id"]),
            title=row["title"],
            summary=row.get("summary_short") or row.get("summary") or "",
            published_at=datetime.fromisoformat(row["published_at"]),
        )
        for row in rows
    ]
    return sorted(articles, key=lambda a: a.published_at)
