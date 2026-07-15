"""wiki 테스트 — 링크·목차 정합 점검 + 노트 자동 생성. 네트워크 없이 동작."""

import re
from datetime import datetime
from pathlib import Path

from plick_embedding.eval.scoring import MergeCase, PairwiseScore, ScoreResult, SplitCase
from plick_embedding.pipeline.articles import Article
from plick_embedding.report.report import ExperimentConfig
from plick_embedding.report.wiki import note_stem, write_wiki_note
from plick_embedding.settings import PROJECT_ROOT

WIKI = PROJECT_ROOT / "wiki"
LINK = re.compile(r"\[\[([^\]]+)\]\]")


def _note_stems(wiki: Path) -> set[str]:
    return {p.stem for p in wiki.rglob("*.md")}


def _links_in(text: str) -> list[str]:
    # 인라인 코드(`...`) 안의 [[예시]]는 실제 링크가 아니므로 제외
    text = re.sub(r"`[^`]*`", "", text)
    # [[대상|별칭]] / [[대상]] → 대상만
    return [m.split("|")[0].strip() for m in LINK.findall(text)]


def test_no_broken_links() -> None:
    """실 wiki의 모든 [[링크]] 대상 노트가 존재한다 (templates/ 제외 — 자리표시자)."""
    stems = _note_stems(WIKI)
    broken: list[str] = []
    for md in WIKI.rglob("*.md"):
        if "templates" in md.parts:
            continue
        for target in _links_in(md.read_text(encoding="utf-8")):
            if target not in stems:
                broken.append(f"{md.name} → [[{target}]]")
    assert not broken, f"깨진 링크: {broken}"


def test_index_lists_every_experiment() -> None:
    """experiments/의 모든 노트가 목차(00-INDEX)에 링크로 올라 있다."""
    index = (WIKI / "00-INDEX.md").read_text(encoding="utf-8")
    listed = set(_links_in(index))
    for note in (WIKI / "experiments").glob("*.md"):
        assert note.stem in listed, f"목차에 없는 실험 노트: {note.stem}"


def _sample_config() -> ExperimentConfig:
    return ExperimentConfig(
        model="gemini-embedding-001",
        task_type="SEMANTIC_SIMILARITY",
        dim=768,
        threshold=0.85,
        window_hours=24.0,
        input_path="data/articles.json",
        n_articles=90,
    )


def test_note_stem_format() -> None:
    stem = note_stem(_sample_config(), datetime(2026, 7, 15, 10, 0))
    assert stem == "2026-07-15_articles90_gemini-d768_SEMANTIC_0.85_24h"


def test_write_wiki_note_creates_note_and_index_row(tmp_path) -> None:
    wiki = tmp_path / "wiki"
    (wiki / "experiments").mkdir(parents=True)
    (wiki / "00-INDEX.md").write_text(
        "# 목차\n\n## 실험 기록 (experiments/)\n\n"
        "| 날짜 | 노트 | 구성 | 결과 |\n|------|------|------|------|\n",
        encoding="utf-8",
    )
    config = _sample_config()
    articles = [
        Article("a", "제목 A", "", datetime(2026, 7, 15, 1, 0)),
        Article("b", "제목 B", "", datetime(2026, 7, 15, 2, 0)),
    ]
    score = ScoreResult(
        n_labeled=2,
        n_unlabeled=0,
        n_truth_issues=1,
        n_pred_clusters=1,
        ari=0.9071,
        pairwise=PairwiseScore(0.94, 0.88, 0.91, 80, 5, 11),
        overmerges=[MergeCase(0, {"x": ["a 제목 A"], "y": ["b 제목 B"]})],
        oversplits=[SplitCase("z", {0: ["a 제목 A"], 1: ["b 제목 B"]})],
    )
    run_at = datetime(2026, 7, 15, 10, 20)

    note = write_wiki_note(config, [articles], run_at, score=score, wiki_dir=wiki)

    body = note.read_text(encoding="utf-8")
    assert note.name == "2026-07-15_articles90_gemini-d768_SEMANTIC_0.85_24h.md"
    assert "ari: 0.9071" in body  # 머리말에 점수
    assert "task_type: SEMANTIC_SIMILARITY" in body  # 머리말에 조건
    assert "잘못 합침" in body  # 대표 사례
    index = (wiki / "00-INDEX.md").read_text(encoding="utf-8")
    assert "[[2026-07-15_articles90_gemini-d768_SEMANTIC_0.85_24h]]" in index  # 목차 등록


def test_write_wiki_note_replaces_existing_row(tmp_path) -> None:
    """같은 노트를 다시 쓰면 목차 행이 중복되지 않고 교체된다."""
    wiki = tmp_path / "wiki"
    (wiki / "experiments").mkdir(parents=True)
    (wiki / "00-INDEX.md").write_text(
        "## 실험 기록 (experiments/)\n\n"
        "| 날짜 | 노트 | 구성 | 결과 |\n|------|------|------|------|\n",
        encoding="utf-8",
    )
    config = _sample_config()
    run_at = datetime(2026, 7, 15, 10, 20)
    for _ in range(2):
        write_wiki_note(config, [], run_at, score=None, wiki_dir=wiki)
    index = (wiki / "00-INDEX.md").read_text(encoding="utf-8")
    assert index.count("[[2026-07-15_articles90_gemini-d768_SEMANTIC_0.85_24h]]") == 1
