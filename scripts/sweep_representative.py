"""묶음 대표값 3안 비교 — 순차(하나씩) 묶기에서 대표값만 바꿔 채점한다.

평균(centroid) / 최신(latest) / 첫 기사(seed) 세 방식을 같은 임베딩·설정으로 돌려
점수(ARI·잘못 합침·잘못 나뉨)와 방식별 잘못 합침 사례를 나란히 보여준다. 결과
파일은 만들지 않고 출력만 한다(캐시된 임베딩만 쓰므로 API 비용 0).

예: uv run python scripts/sweep_representative.py --threshold 0.86
"""

import argparse
from datetime import timedelta
from pathlib import Path

from plick_embedding.eval.labels import load_labels
from plick_embedding.eval.scoring import score as score_clusters
from plick_embedding.pipeline.articles import load_articles
from plick_embedding.pipeline.incremental import REPRESENTATIVES, cluster_incrementally
from plick_embedding.providers.base import EmbeddingConfig
from plick_embedding.providers.gemini import GeminiEmbeddingProvider
from plick_embedding.settings import PROJECT_ROOT, load_settings

LABELS = {"centroid": "평균", "latest": "최신", "seed": "첫 기사"}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="순차 묶기 대표값 3안 비교 (Gemini 선정 구성 기본)")
    p.add_argument("--task-type", default="SEMANTIC_SIMILARITY")
    p.add_argument("--dim", type=int, default=768)
    p.add_argument("--threshold", type=float, default=0.86)
    p.add_argument("--window", type=float, default=24.0, help="비교 시간 범위(시간)")
    p.add_argument("--input", type=Path, default=PROJECT_ROOT / "data" / "articles.json")
    p.add_argument(
        "--labels", type=Path, default=PROJECT_ROOT / "data" / "labels" / "articles90.json"
    )
    return p


def main() -> None:
    args = build_parser().parse_args()
    settings = load_settings()
    if not settings.has_gemini:
        raise SystemExit("GEMINI_API_KEY가 없습니다 (.env 확인).")

    articles = load_articles(args.input)
    labels = load_labels(args.labels)
    window = timedelta(hours=args.window)
    cfg = EmbeddingConfig(model="gemini-embedding-001", task_type=args.task_type, dim=args.dim)
    provider = GeminiEmbeddingProvider(cfg, api_key=settings.gemini_api_key)
    emb = provider.embed([a.embed_text for a in articles])
    published = [a.published_at for a in articles]

    scores = {}
    for rep in REPRESENTATIVES:
        pred = cluster_incrementally(
            emb, published, threshold=args.threshold, window=window, representative=rep
        )
        scores[rep] = score_clusters(articles, pred, labels)

    print(f"\n기사 {len(articles)}건 · 기준값 {args.threshold} · 최근 {int(args.window)}시간\n")
    print("| 대표값 | 묶음 수 | ARI | F1 | 잘못 합침 | 잘못 나뉨 |")
    print("|--------|--------|-----|-----|----------|----------|")
    for rep in REPRESENTATIVES:
        s = scores[rep]
        print(
            f"| {LABELS[rep]}({rep}) | {s.n_pred_clusters} | {s.ari:.4f} | "
            f"{s.pairwise.f1:.4f} | {len(s.overmerges)} | {len(s.oversplits)} |"
        )

    for rep in REPRESENTATIVES:
        s = scores[rep]
        print(f"\n== {LABELS[rep]}({rep}) 잘못 합침 {len(s.overmerges)}건 ==")
        for case in s.overmerges:
            print(f"  묶음 #{case.pred_cluster}: {' + '.join(case.members_by_issue)}")


if __name__ == "__main__":
    main()
