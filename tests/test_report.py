"""report 테스트 — 결과 폴더 구조와 요약 수치."""

import json
from datetime import datetime
from pathlib import Path

import numpy as np

from plick_embedding.pipeline.articles import Article
from plick_embedding.report.report import ExperimentConfig, write_report

CONFIG = ExperimentConfig(
    model="gemini-embedding-001",
    task_type="SEMANTIC_SIMILARITY",
    dim=768,
    threshold=0.85,
    window_hours=24.0,
    input_path="data/articles.json",
    n_articles=3,
)


def _article(id_: str, hour: int) -> Article:
    return Article(
        id=id_,
        title=f"기사 {id_}",
        summary="요약",
        published_at=datetime(2026, 6, 29, hour, 0),
    )


def test_write_report_creates_run_dir(tmp_path: Path) -> None:
    articles = [_article("a", 9), _article("b", 10), _article("c", 11)]
    labels = np.array([0, 0, 1])  # 중복 묶음 1개(a,b) + 단독 1개(c)

    run_dir = write_report(
        CONFIG,
        articles,
        labels,
        results_dir=tmp_path,
        run_at=datetime(2026, 7, 14, 12, 0),
    )

    assert run_dir == tmp_path / "20260714_120000"
    result = json.loads((run_dir / "result.json").read_text(encoding="utf-8"))
    assert result["n_clusters"] == 2
    assert result["n_dup_groups"] == 1
    assert len(result["clusters"][0]) == 2  # 큰 묶음이 먼저

    config = json.loads((run_dir / "config.json").read_text(encoding="utf-8"))
    assert config["threshold"] == 0.85

    report = (run_dir / "report.md").read_text(encoding="utf-8")
    assert "이슈(군집) 수: **2**" in report
    assert "중복 묶음(2건 이상) 수: **1**" in report
