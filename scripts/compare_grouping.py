"""중복 묶기 처리 방식 비교 — 배치(한꺼번에) vs 순차(하나씩)를 같은 데이터로 채점.

동일한 임베딩·설정 위에서 두 방식을 각각 돌려 점수(ARI·잘못 합침·잘못 나뉨)와
두 방식이 다르게 묶은 사례를 나란히 보여준다. 결과 파일은 만들지 않고 출력만 한다
(캐시된 임베딩만 쓰므로 API 비용 0).

예: uv run python scripts/compare_grouping.py --threshold 0.86 --representative centroid
"""

import argparse
from datetime import timedelta
from pathlib import Path

from sklearn.metrics import adjusted_rand_score

from plick_embedding.eval.labels import load_labels
from plick_embedding.eval.scoring import ScoreResult
from plick_embedding.eval.scoring import score as score_clusters
from plick_embedding.pipeline.articles import load_articles
from plick_embedding.pipeline.clustering import cluster_embeddings
from plick_embedding.pipeline.incremental import cluster_incrementally
from plick_embedding.pipeline.window import split_clusters_by_window
from plick_embedding.providers.base import EmbeddingConfig
from plick_embedding.providers.gemini import GeminiEmbeddingProvider
from plick_embedding.settings import PROJECT_ROOT, load_settings


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="배치 vs 순차 중복 묶기 비교 (Gemini 선정 구성 기본)")
    p.add_argument("--task-type", default="SEMANTIC_SIMILARITY")
    p.add_argument("--dim", type=int, default=768)
    p.add_argument("--threshold", type=float, default=0.86)
    p.add_argument("--window", type=float, default=24.0, help="비교 시간 범위(시간)")
    p.add_argument("--representative", default="centroid")
    p.add_argument("--input", type=Path, default=PROJECT_ROOT / "data" / "articles.json")
    p.add_argument(
        "--labels", type=Path, default=PROJECT_ROOT / "data" / "labels" / "articles90.json"
    )
    return p


def _row(name: str, s: ScoreResult) -> str:
    p = s.pairwise
    return (
        f"| {name} | {s.n_pred_clusters} | {s.ari:.4f} | {p.f1:.4f} | "
        f"{len(s.overmerges)} | {len(s.oversplits)} |"
    )


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

    # 배치: 전역 군집화 → 시간 범위로 나누기
    batch = split_clusters_by_window(
        cluster_embeddings(emb, threshold=args.threshold), published, window
    )
    # 순차: 발행 시각 순으로 하나씩
    online = cluster_incrementally(
        emb, published, threshold=args.threshold, window=window, representative=args.representative
    )

    s_batch = score_clusters(articles, batch, labels)
    s_online = score_clusters(articles, online, labels)
    between = adjusted_rand_score(batch, online)

    print(f"\n기사 {len(articles)}건 · 기준값 {args.threshold} · 대표값 {args.representative}\n")
    print("| 방식 | 묶음 수 | ARI(정답 대비) | F1 | 잘못 합침 | 잘못 나뉨 |")
    print("|------|--------|--------------|-----|----------|----------|")
    print(_row("배치(한꺼번에)", s_batch))
    print(_row("순차(하나씩)", s_online))
    print(f"\n두 방식이 얼마나 같게 묶었나 (ARI 배치 vs 순차): {between:.4f}\n")

    # 순차에서만 새로 쪼개진 사건 (배치는 한 묶음, 순차는 여러 묶음)
    batch_split = {c.issue for c in s_batch.oversplits}
    online_split = {c.issue for c in s_online.oversplits}
    print("== 순차에서만 새로 쪼개진 사건 (배치는 안 쪼갬) ==")
    newly = sorted(online_split - batch_split)
    if not newly:
        print("  없음")
    for case in s_online.oversplits:
        if case.issue not in newly:
            continue
        print(f"\n[{case.issue}] 순차에서 묶음 {len(case.members_by_cluster)}개로 나뉨:")
        for cid, members in case.members_by_cluster.items():
            print(f"   묶음#{cid}: {', '.join(members)}")

    # 잘못 합침 상세 (순차가 배치보다 많은 게 핵심)
    n_bm, n_om = len(s_batch.overmerges), len(s_online.overmerges)
    print(f"\n== 잘못 합침: 배치 {n_bm}건 · 순차 {n_om}건 ==")
    for name, s in (("배치", s_batch), ("순차", s_online)):
        for case in s.overmerges:
            issues = " + ".join(case.members_by_issue)
            print(f"  [{name}] 묶음 #{case.pred_cluster}: {issues}")


if __name__ == "__main__":
    main()
