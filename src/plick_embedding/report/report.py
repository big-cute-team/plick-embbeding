"""실험 결과 리포트 — 실행 1회 = results/<타임스탬프>/ 하나.

config(조건)와 result(묶음 결과)를 JSON으로 저장하고, Confluence 실험 기록
양식에 맞춘 report.md를 함께 남긴다.
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

import numpy as np

from plick_embedding.eval.scoring import ScoreResult
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
    score: ScoreResult | None = None,
) -> Path:
    """results/<타임스탬프>/에 config·result·report를 저장하고 폴더 경로를 반환한다.

    score가 주어지면 정량 평가 섹션과 scores.json을 함께 남긴다.
    """
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
    if score is not None:
        (run_dir / "scores.json").write_text(
            json.dumps(asdict(score), ensure_ascii=False, indent=2), encoding="utf-8"
        )
    (run_dir / "report.md").write_text(
        render_markdown(config, clusters, run_at, score), encoding="utf-8"
    )
    return run_dir


def render_markdown(
    config: ExperimentConfig,
    clusters: list[list[Article]],
    run_at: datetime,
    score: ScoreResult | None = None,
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
    ]
    if score is not None:
        lines += _render_score(score)
    lines += ["## 중복 묶음 상세", ""]
    for i, cluster in enumerate(dup_groups, start=1):
        lines.append(f"### 묶음 {i} ({len(cluster)}건)")
        lines.append("")
        for article in sorted(cluster, key=lambda a: a.published_at):
            stamp = article.published_at.strftime("%m-%d %H:%M")
            lines.append(f"- [{stamp}] ({article.id}) {article.title}")
        lines.append("")
    return "\n".join(lines)


def _render_score(score: ScoreResult) -> list[str]:
    """정량 평가 섹션 (정답 대비 ARI·쌍 단위·오병합·과분할)."""
    p = score.pairwise
    lines = [
        "## 정량 평가 (정답 대비)",
        "",
        f"- 채점 대상: 정답 있는 기사 **{score.n_labeled}건** "
        f"(정답 없음 {score.n_unlabeled}건 제외), 정답 이슈 {score.n_truth_issues}개 "
        f"vs 예측 묶음 {score.n_pred_clusters}개",
        f"- **ARI**: {score.ari:.4f}",
        f"- **쌍 단위**: 정밀도 {p.precision:.4f} · 재현율 {p.recall:.4f} · "
        f"F1 {p.f1:.4f} (TP {p.tp} · FP {p.fp} · FN {p.fn})",
        "",
        f"### 오병합 (서로 다른 이슈가 한 묶음, {len(score.overmerges)}건)",
        "",
    ]
    if not score.overmerges:
        lines += ["- 없음", ""]
    for case in score.overmerges:
        n_issues = len(case.members_by_issue)
        lines.append(f"- 예측 묶음 #{case.pred_cluster} — 정답 이슈 {n_issues}개 혼합")
        for issue, members in case.members_by_issue.items():
            lines.append(f"  - `{issue}`: {', '.join(members)}")
    lines.append("")
    lines += [f"### 과분할 (한 이슈가 여러 묶음, {len(score.oversplits)}건)", ""]
    if not score.oversplits:
        lines += ["- 없음", ""]
    for case in score.oversplits:
        lines.append(f"- `{case.issue}` — 예측 묶음 {len(case.members_by_cluster)}개로 분할")
        for cluster, members in case.members_by_cluster.items():
            lines.append(f"  - 묶음 #{cluster}: {', '.join(members)}")
    lines.append("")
    return lines


def _size_distribution(clusters: list[list[Article]]) -> str:
    counts: dict[int, int] = {}
    for cluster in clusters:
        counts[len(cluster)] = counts.get(len(cluster), 0) + 1
    return ", ".join(f"{size}건×{n}" for size, n in sorted(counts.items()))
