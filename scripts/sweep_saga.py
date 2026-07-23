"""여러 날 이어지는 이슈(사가) 대응 비교 — 범위 늘리기 vs 수명 연장.

순차 묶기(첫 기사) 위에서 두 대응을 여러 값으로 돌려 채점한다:
① 비교 시간 범위 자체를 늘리기 (24 → 36/48/72h)
② 글이 2건 이상 붙은 묶음만 수명을 늘리기 (24h 유지 + 확인된 묶음만 48/72h)

실제로 갈렸던 사가가 몇 개 묶음으로 나뉘는지도 함께 본다. 캐시된 임베딩만
쓰므로 API 비용 0.

예: uv run python scripts/sweep_saga.py
"""

import argparse
from datetime import timedelta
from pathlib import Path

from plick_embedding.eval.labels import load_labels
from plick_embedding.eval.scoring import ScoreResult
from plick_embedding.eval.scoring import score as score_clusters
from plick_embedding.pipeline.articles import load_articles
from plick_embedding.pipeline.incremental import cluster_incrementally
from plick_embedding.providers.base import EmbeddingConfig
from plick_embedding.providers.gemini import GeminiEmbeddingProvider
from plick_embedding.settings import PROJECT_ROOT, load_settings

# 앞선 실험에서 24h 때문에 갈렸던 사가들 (몇 조각으로 나뉘는지 추적)
SAGAS = [
    "ederson_manutd_collapse",
    "alonso_chelsea_arrival",
    "england_training_guehi_rice_james",
    "spence_norway_match",
]

# (이름, window 시간, extended_window 시간 또는 None)
CONFIGS = [
    ("기준선 24h", 24, None),
    ("범위 36h", 36, None),
    ("범위 48h", 48, None),
    ("범위 72h", 72, None),
    ("수명연장 24→48h", 24, 48),
    ("수명연장 24→72h", 24, 72),
]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="사가 대응 비교 (Gemini 선정 구성, 대표값 첫 기사)")
    p.add_argument("--task-type", default="SEMANTIC_SIMILARITY")
    p.add_argument("--dim", type=int, default=768)
    p.add_argument("--threshold", type=float, default=0.86)
    p.add_argument("--input", type=Path, default=PROJECT_ROOT / "data" / "articles.json")
    p.add_argument(
        "--labels", type=Path, default=PROJECT_ROOT / "data" / "labels" / "articles90.json"
    )
    return p


def _saga_pieces(articles, pred_labels, label_set, issue: str) -> int:
    """정답 issue에 속한 기사들이 예측에서 몇 개 묶음으로 나뉘었나."""
    clusters = {
        int(p)
        for a, p in zip(articles, pred_labels, strict=True)
        if label_set.issue_of(a.id) == issue
    }
    return len(clusters)


def main() -> None:
    args = build_parser().parse_args()
    settings = load_settings()
    if not settings.has_gemini:
        raise SystemExit("GEMINI_API_KEY가 없습니다 (.env 확인).")

    articles = load_articles(args.input)
    labels = load_labels(args.labels)
    cfg = EmbeddingConfig(model="gemini-embedding-001", task_type=args.task_type, dim=args.dim)
    emb = GeminiEmbeddingProvider(cfg, api_key=settings.gemini_api_key).embed(
        [a.embed_text for a in articles]
    )
    published = [a.published_at for a in articles]

    rows: list[tuple[str, ScoreResult, dict[str, int]]] = []
    for name, win, ext in CONFIGS:
        pred = cluster_incrementally(
            emb,
            published,
            threshold=args.threshold,
            window=timedelta(hours=win),
            representative="seed",
            extended_window=timedelta(hours=ext) if ext else None,
            extend_after=2,
        )
        s = score_clusters(articles, pred, labels)
        pieces = {issue: _saga_pieces(articles, pred, labels, issue) for issue in SAGAS}
        rows.append((name, s, pieces))

    print(f"\n기사 {len(articles)}건 · 기준값 {args.threshold} · 대표값 첫 기사\n")
    print("| 대응 | 묶음 수 | ARI | F1 | 잘못 합침 | 잘못 나뉨 |")
    print("|------|--------|-----|-----|----------|----------|")
    for name, s, _ in rows:
        print(
            f"| {name} | {s.n_pred_clusters} | {s.ari:.4f} | {s.pairwise.f1:.4f} | "
            f"{len(s.overmerges)} | {len(s.oversplits)} |"
        )

    print("\n== 사가가 몇 조각으로 나뉘나 (1이면 안 갈림) ==")
    header = "| 대응 | " + " | ".join(s.replace("_", " ")[:14] for s in SAGAS) + " |"
    print(header)
    print("|" + "---|" * (len(SAGAS) + 1))
    for name, _, pieces in rows:
        print(f"| {name} | " + " | ".join(str(pieces[s]) for s in SAGAS) + " |")


if __name__ == "__main__":
    main()
