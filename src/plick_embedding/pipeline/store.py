"""벡터 저장소 — 로컬 파일(JSONL) 한 곳에 벡터 + 메타 + 어느 이슈인지를 담는다 (T01 결정).

한 줄 = 기사 1건. 벡터와 함께 "어떤 모델·용도·차원으로 만들었는지"(model·task_type·
dim·normalized)와 발행 시각·issue_id를 같이 저장한다. 규모가 작아(하루 ~150건)
파일 전체를 메모리에 올려 두고, 바뀌면 통째로 다시 쓴다.

운영(plick-ai/admin-server)에선 이 자리를 Postgres + 벡터DB로 바꾼다. 그때 갈아끼우기
쉽게, 넣기/전체 읽기/이미 있는 id 확인/이슈 적기만 공개한다(Store 경계).
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np


@dataclass
class StoredArticle:
    """저장소 한 줄 — 벡터와 그 벡터를 어떻게 만들었는지, 어느 이슈인지."""

    id: str
    published_at: datetime
    vector: np.ndarray
    model: str
    task_type: str
    dim: int
    normalized: bool
    issue_id: str | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "published_at": self.published_at.isoformat(),
            "vector": [float(x) for x in self.vector],
            "model": self.model,
            "task_type": self.task_type,
            "dim": self.dim,
            "normalized": self.normalized,
            "issue_id": self.issue_id,
        }

    @classmethod
    def from_dict(cls, row: dict) -> "StoredArticle":
        return cls(
            id=str(row["id"]),
            published_at=datetime.fromisoformat(row["published_at"]),
            vector=np.array(row["vector"], dtype=np.float32),
            model=row["model"],
            task_type=row["task_type"],
            dim=row["dim"],
            normalized=row["normalized"],
            issue_id=row.get("issue_id"),
        )


class VectorStore:
    """로컬 파일 벡터 저장소. 넣기/전체 읽기/이미 있는 id 확인/이슈 적기."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._by_id: dict[str, StoredArticle] = {}
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    record = StoredArticle.from_dict(json.loads(line))
                    self._by_id[record.id] = record

    def known_ids(self) -> set[str]:
        """이미 저장된(=처리한) 기사 id 집합."""
        return set(self._by_id)

    def add(self, records: list[StoredArticle]) -> None:
        """새 기사 벡터를 저장한다 (이미 있는 id는 덮어쓰지 않고 무시)."""
        for record in records:
            self._by_id.setdefault(record.id, record)
        self._save()

    def set_issues(self, mapping: dict[str, str]) -> None:
        """묶기 결과(기사 id → issue_id)를 저장소에 적는다."""
        for article_id, issue_id in mapping.items():
            if article_id in self._by_id:
                self._by_id[article_id].issue_id = issue_id
        self._save()

    def all(self) -> list[StoredArticle]:
        """저장된 전체를 발행 시각 순으로 반환한다 (묶기 입력용)."""
        return sorted(self._by_id.values(), key=lambda r: r.published_at)

    def _save(self) -> None:
        """임시 파일에 먼저 쓰고 한 번에 바꿔치기(원자적) — 쓰다 끊겨도 기존 저장이 안 깨진다."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            json.dumps(r.to_dict(), ensure_ascii=False)
            for r in sorted(self._by_id.values(), key=lambda r: r.published_at)
        ]
        tmp = self.path.with_name(self.path.name + ".tmp")
        tmp.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        os.replace(tmp, self.path)  # 같은 폴더 내 교체는 원자적
