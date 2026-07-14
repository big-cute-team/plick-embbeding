"""실험 결과 리포트 — 실행 1회 = results/<타임스탬프>/ 하나.

config(조건)와 result(묶음 결과)를 JSON으로 저장하고, Confluence 실험 기록
양식에 맞춘 report.md를 함께 남긴다.
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

import numpy as np

from plick_embedding.pipeline.articles import Article
from plick_embedding.settings import PROJECT_ROOT

DEFAULT_RESULTS_DIR = PROJECT_ROOT / "results"


@dataclass(frozen=True)
class ExperimentConfig:
    """실행 1회의 전체 조건 — 이 값만 있으면 같은 실험을 재현할 수 있다."""

    model: str
    task_type: str
    dim: int
    threshold: float
    window_hours: float
    input_path: str
    n_articles: int


def build_clusters(articles: list[Article], labels: np.ndarray) -> list[list[Article]]:
    """라벨을 기사 묶음 목록으로 바꾼다 (큰 묶음 → 이른 발행 순)."""
    by_label: dict[int, list[Article]] = {}
    for article, label in zip(articles, labels, strict=True):
        by_label.setdefault(int(label), []).append(article)
    return sorted(by_label.values(), key=lambda c: (-len(c), min(a.published_at for a in c)))


def write_report(
    config: ExperimentConfig,
    articles: list[Article],
    labels: np.ndarray,
    results_dir: Path = DEFAULT_RESULTS_DIR,
    run_at: datetime | None = None,
) -> Path:
    """results/<타임스탬프>/에 config·result·report를 저장하고 폴더 경로를 반환한다."""
    run_at = run_at or datetime.now()
    run_dir = results_dir / run_at.strftime("%Y%m%d_%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=False)

    clusters = build_clusters(articles, labels)
    dup_groups = [c for c in clusters if len(c) >= 2]

    (run_dir / "config.json").write_text(
        json.dumps(asdict(config), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    result = {
        "n_articles": len(articles),
        "n_clusters": len(clusters),
        "n_dup_groups": len(dup_groups),
        "clusters": [
            [
                {"id": a.id, "title": a.title, "published_at": a.published_at.isoformat()}
                for a in cluster
            ]
            for cluster in clusters
        ],
    }
    (run_dir / "result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (run_dir / "report.md").write_text(render_markdown(config, clusters, run_at), encoding="utf-8")
    return run_dir


def render_markdown(
    config: ExperimentConfig, clusters: list[list[Article]], run_at: datetime
) -> str:
    """Confluence 실험 기록 양식에 붙여넣을 수 있는 텍스트를 만든다."""
    dup_groups = [c for c in clusters if len(c) >= 2]
    lines = [
        f"# 임베딩 중복 묶기 실험 — {run_at.strftime('%Y-%m-%d %H:%M')}",
        "",
        "## 실험 조건",
        "",
        "| 항목 | 값 |",
        "|------|-----|",
        f"| 모델 | {config.model} |",
        f"| task_type | {config.task_type} |",
        f"| 차원 | {config.dim} |",
        f"| 임계값 | {config.threshold} |",
        f"| 윈도우 | {config.window_hours}h |",
        f"| 입력 | {config.input_path} ({config.n_articles}건) |",
        "",
        "## 결과 요약",
        "",
        f"- 이슈(군집) 수: **{len(clusters)}**",
        f"- 중복 묶음(2건 이상) 수: **{len(dup_groups)}**",
        f"- 묶음 크기 분포: {_size_distribution(clusters)}",
        "",
        "## 중복 묶음 상세",
        "",
    ]
    for i, cluster in enumerate(dup_groups, start=1):
        lines.append(f"### 묶음 {i} ({len(cluster)}건)")
        lines.append("")
        for article in sorted(cluster, key=lambda a: a.published_at):
            stamp = article.published_at.strftime("%m-%d %H:%M")
            lines.append(f"- [{stamp}] ({article.id}) {article.title}")
        lines.append("")
    return "\n".join(lines)


def _size_distribution(clusters: list[list[Article]]) -> str:
    counts: dict[int, int] = {}
    for cluster in clusters:
        counts[len(cluster)] = counts.get(len(cluster), 0) + 1
    return ", ".join(f"{size}건×{n}" for size, n in sorted(counts.items()))
