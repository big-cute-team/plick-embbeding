"""실험 노트 자동 생성 — 실험을 돌리면 wiki/experiments/에 노트 1개를 만들고
목차(00-INDEX.md)의 실험 기록 표에 한 줄 추가한다.

노트는 그것만 읽어도 이해되게 쓴다 (results/는 git에 안 올라가므로 점수·대표
사례를 본문에 직접 담는다). 형식·규칙은 wiki/00-INDEX.md "위키 작성 규칙" 참조.
"""

from datetime import datetime
from pathlib import Path

from plick_embedding.eval.scoring import ScoreResult
from plick_embedding.pipeline.articles import Article
from plick_embedding.report.report import ExperimentConfig
from plick_embedding.settings import PROJECT_ROOT

DEFAULT_WIKI_DIR = PROJECT_ROOT / "wiki"
_TABLE_HEADER = "| 날짜 | 노트 | 구성 | 결과 |"


def _task_label(task_type: str) -> str:
    """SEMANTIC_SIMILARITY → SEMANTIC 처럼 앞 토큰만 (노트 이름 짧게)."""
    return task_type.split("_")[0]


def _dataset_slug(config: ExperimentConfig) -> str:
    """입력 파일명 + 건수 → 예: articles90."""
    stem = Path(config.input_path).stem
    return f"{stem}{config.n_articles}"


def note_stem(config: ExperimentConfig, run_at: datetime) -> str:
    """노트 파일명(확장자 제외) = 날짜_데이터셋_task_임계_비교범위."""
    window = int(config.window_hours) if config.window_hours.is_integer() else config.window_hours
    return (
        f"{run_at:%Y-%m-%d}_{_dataset_slug(config)}_"
        f"{_task_label(config.task_type)}_{config.threshold}_{window}h"
    )


def write_wiki_note(
    config: ExperimentConfig,
    clusters: list[list[Article]],
    run_at: datetime,
    score: ScoreResult | None = None,
    run_dir: Path | None = None,
    wiki_dir: Path = DEFAULT_WIKI_DIR,
) -> Path:
    """wiki/experiments/에 노트를 쓰고 목차에 등록한 뒤 노트 경로를 반환한다."""
    stem = note_stem(config, run_at)
    note_path = wiki_dir / "experiments" / f"{stem}.md"
    note_path.parent.mkdir(parents=True, exist_ok=True)
    note = _render_note(config, clusters, run_at, score, run_dir, stem)
    note_path.write_text(note, encoding="utf-8")
    _update_index(wiki_dir, config, run_at, score, stem)
    return note_path


def _render_note(
    config: ExperimentConfig,
    clusters: list[list[Article]],
    run_at: datetime,
    score: ScoreResult | None,
    run_dir: Path | None,
    stem: str,
) -> str:
    dup_groups = [c for c in clusters if len(c) >= 2]
    ari = f"{score.ari:.4f}" if score else "null"
    f1 = f"{score.pairwise.f1:.4f}" if score else "null"
    window = int(config.window_hours) if config.window_hours.is_integer() else config.window_hours
    lines = [
        "---",
        f"model: {config.model}",
        f"task_type: {config.task_type}",
        f"dim: {config.dim}",
        f"threshold: {config.threshold}",
        f"window_hours: {window}",
        f"dataset: {_dataset_slug(config)} ({config.n_articles}건)",
        f"ari: {ari}",
        f"pairwise_f1: {f1}",
        f"date: {run_at:%Y-%m-%d %H:%M}",
        "author: 자동 생성",
        "---",
        "",
        f"# {stem}",
        "",
        "> 실험 실행 시 자동 생성된 노트. `results/`는 git에 안 올라가므로",
        "> 점수·대표 사례를 아래에 직접 담는다.",
        "",
        "## 조건",
        "",
        "| 항목 | 값 |",
        "|------|-----|",
        f"| 모델 | {config.model} |",
        f"| task_type | {config.task_type} ([[task_type]]) |",
        f"| 차원 / 정규화 | {config.dim} / L2 |",
        f"| 임계값 | {config.threshold} |",
        f"| 비교 범위 | 최근 {window}시간만 비교 ([[최근 24시간만 비교]]) |",
        f"| 입력 데이터 | {config.input_path} ({config.n_articles}건) |",
        "",
        "## 결과",
        "",
        f"- 이슈(묶음) 수 / 중복 묶음 수: **{len(clusters)}** / **{len(dup_groups)}**",
    ]
    if score:
        p = score.pairwise
        lines += [
            f"- 정답과 얼마나 일치하나 (ARI): **{score.ari:.4f}** "
            "([[정답과 얼마나 일치하나 (ARI)]])",
            f"- 묶음 정확도(기사 쌍): 맞게 묶은 비율 {p.precision:.4f} · "
            f"찾아낸 비율 {p.recall:.4f} · 종합 {p.f1:.4f}",
        ]
    lines += ["", "## 대표 사례", ""]
    lines += _sample_cases(dup_groups, score)
    lines += [
        "",
        "## 해석 · 다음 시도",
        "",
        "- (해석을 채우세요)",
        "",
        "## 참고",
        "",
        f"- 산출물: `{run_dir}`" if run_dir else "- 산출물: `results/<타임스탬프>/`",
        f"- 모델: [[{config.model}]]",
        "",
    ]
    return "\n".join(lines)


def _sample_cases(dup_groups: list[list[Article]], score: ScoreResult | None) -> list[str]:
    lines: list[str] = []
    if dup_groups:
        biggest = max(dup_groups, key=len)
        titles = ", ".join(a.title for a in sorted(biggest, key=lambda a: a.published_at)[:3])
        lines.append(f"- 가장 큰 묶음 ({len(biggest)}건): {titles}")
    if score and score.overmerges:
        c = score.overmerges[0]
        issues = " + ".join(c.members_by_issue)
        lines.append(
            f"- [[잘못 합침과 사가 분할|잘못 합침]] 예: 예측 묶음 #{c.pred_cluster} = {issues}"
        )
    if score and score.oversplits:
        lines.append(
            f"- [[잘못 합침과 사가 분할|잘못 나뉨]] 예: `{score.oversplits[0].issue}`가 "
            f"{len(score.oversplits[0].members_by_cluster)}개 묶음으로 나뉨"
        )
    if not lines:
        lines.append("- (중복 묶음 없음)")
    return lines


def _update_index(
    wiki_dir: Path,
    config: ExperimentConfig,
    run_at: datetime,
    score: ScoreResult | None,
    stem: str,
) -> None:
    """목차의 실험 기록 표에 행을 추가/갱신한다 (같은 노트면 교체)."""
    index_path = wiki_dir / "00-INDEX.md"
    if not index_path.exists():
        return
    result = (
        f"ARI {score.ari:.4f} · F1 {score.pairwise.f1:.4f}" if score else "이슈/묶음 수는 노트 참조"
    )
    config_desc = f"{_task_label(config.task_type)} · {config.threshold} · {_dataset_slug(config)}"
    row = f"| {run_at:%Y-%m-%d} | [[{stem}]] | {config_desc} | {result} |"

    lines = index_path.read_text(encoding="utf-8").splitlines()
    link_token = f"[[{stem}]]"
    # 이미 있으면 그 줄을 교체
    for i, line in enumerate(lines):
        if link_token in line and line.lstrip().startswith("|"):
            lines[i] = row
            index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    # 없으면 표 구분선 바로 아래(최신이 위)에 삽입
    for i, line in enumerate(lines):
        if line.strip() == _TABLE_HEADER:
            lines.insert(i + 2, row)  # 헤더 + 구분선 다음
            index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
