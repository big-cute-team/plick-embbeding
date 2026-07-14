"""정답 라벨 로드 — 기사 id → 이슈 id 매핑.

정답지 형식(`data/labels/*.json`): 평탄한 JSON 객체 하나.

    {"6894": "santos_manutd", "6913": "santos_manutd", ...}

키는 기사 id(문자열), 값은 그 기사가 속한 이슈 id(문자열)다. 같은 이슈 id를
가진 기사들이 정답 군집 하나를 이룬다. 실험이 예측한 군집을 이 정답과 비교해
점수를 낸다 (eval/scoring.py).
"""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LabelSet:
    """기사 id → 이슈 id 정답 매핑."""

    issue_by_article: dict[str, str]

    def issue_of(self, article_id: str) -> str | None:
        return self.issue_by_article.get(article_id)

    @property
    def n_issues(self) -> int:
        return len(set(self.issue_by_article.values()))

    def missing(self, article_ids: list[str]) -> list[str]:
        """정답이 없는 기사 id 목록 (입력 순서 유지)."""
        return [aid for aid in article_ids if aid not in self.issue_by_article]


def load_labels(path: Path) -> LabelSet:
    """정답지 JSON을 읽어 LabelSet으로 만든다.

    키·값을 모두 문자열로 정규화한다 (JSON 숫자 키 방지). 빈 이슈 id는 거부.
    """
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"정답지는 {{기사 id: 이슈 id}} 객체여야 합니다: {path}")
    issue_by_article: dict[str, str] = {}
    for article_id, issue_id in raw.items():
        issue = str(issue_id).strip()
        if not issue:
            raise ValueError(f"이슈 id가 비어 있습니다 (기사 {article_id}): {path}")
        issue_by_article[str(article_id)] = issue
    return LabelSet(issue_by_article=issue_by_article)
