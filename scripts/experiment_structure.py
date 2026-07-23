"""구조 개선 실험 (KAN-273) — 임베딩 위에 파티션(카테고리 → 주체)을 얹는다.

트랙 B(OpenAI)가 0.8077 → 0.8701로 올린 "분야·핵심 대상으로 먼저 나눠 묶기"를
Gemini 최고 구성(SEMANTIC_SIMILARITY·768·짧은요약 @0.86)에 적용해 효과를 잰다.

단계별로 신호를 하나씩 얹어 채점(임베딩은 캐시 재사용, 새 API 호출 없음):
  0. 기준선   — 전역 군집화 + 최근 24시간만 비교
  1. +카테고리 — 다른 카테고리는 안 묶음 (카테고리별로 나눠 군집화)
  2. +주체     — (카테고리·주체)가 다르면 안 묶음
  3. +주체·완화 — 2 위에서 파티션 안 기준값만 낮춰 봄 (③ 발언 차이 구제 시도)

신호 파일: data/signals/articles90.json (scripts/build_signals.py로 생성).
"""

import argparse
import json
from datetime import timedelta

from plick_embedding.eval.labels import load_labels
from plick_embedding.eval.scoring import score as score_clusters
from plick_embedding.pipeline.articles import embed_texts, load_articles
from plick_embedding.pipeline.clustering import cluster_embeddings, cluster_within_partitions
from plick_embedding.pipeline.window import split_clusters_by_window
from plick_embedding.providers.base import EmbeddingConfig
from plick_embedding.providers.gemini import GeminiEmbeddingProvider
from plick_embedding.settings import PROJECT_ROOT, load_settings


def evaluate(articles, embeddings, partition, threshold, window, labels):
    if partition is None:
        base = cluster_embeddings(embeddings, threshold)
    else:
        base = cluster_within_partitions(embeddings, partition, threshold)
    published = [a.published_at for a in articles]
    final = split_clusters_by_window(base, published, window)
    return score_clusters(articles, final, labels)


def main() -> None:
    parser = argparse.ArgumentParser(prog="experiment_structure")
    parser.add_argument("--dim", type=int, default=768)
    parser.add_argument("--task-type", default="SEMANTIC_SIMILARITY")
    parser.add_argument("--threshold", type=float, default=0.86)
    parser.add_argument("--window", type=float, default=24.0, help="비교 시간 범위(시간)")
    args = parser.parse_args()

    settings = load_settings()
    articles = load_articles(PROJECT_ROOT / "data" / "articles.json")
    labels = load_labels(PROJECT_ROOT / "data" / "labels" / "articles90.json")
    signals = json.loads(
        (PROJECT_ROOT / "data" / "signals" / "articles90.json").read_text(encoding="utf-8")
    )
    window = timedelta(hours=args.window)

    config = EmbeddingConfig(model="gemini-embedding-001", task_type=args.task_type, dim=args.dim)
    provider = GeminiEmbeddingProvider(config, api_key=settings.gemini_api_key)
    embeddings = provider.embed(embed_texts(articles, "title_short"))

    cat = [signals[a.id]["category"] for a in articles]
    subj = [f"{signals[a.id]['category']}|{signals[a.id]['subject_name']}" for a in articles]

    print(
        f"구성: Gemini {args.task_type} d{args.dim} 짧은요약 · "
        f"기준값 {args.threshold} · 창 {args.window}h\n"
    )
    header = f"{'단계':<16}{'ARI':>9}{'F1':>9}{'묶음':>6}{'잘못합침':>9}{'잘못나뉨':>9}"
    print(header)
    print("-" * len(header))

    rows = [
        ("0. 기준선", None, args.threshold),
        ("1. +카테고리", cat, args.threshold),
        ("2. +주체", subj, args.threshold),
    ]
    results = {}
    for name, part, thr in rows:
        r = evaluate(articles, embeddings, part, thr, window, labels)
        results[name] = r
        print(
            f"{name:<16}{r.ari:>9.4f}{r.pairwise.f1:>9.4f}"
            f"{r.n_pred_clusters:>6}{len(r.overmerges):>9}{len(r.oversplits):>9}"
        )

    # 3. +주체·완화 — 파티션 안 기준값을 낮춰 발언 차이(③) 구제 시도
    print()
    best = None
    for thr in [0.85, 0.84, 0.83, 0.82, 0.81, 0.80]:
        r = evaluate(articles, embeddings, subj, thr, window, labels)
        tag = ""
        if best is None or r.ari > best[1]:
            best = (thr, r.ari, r)
            tag = "  ← 최고"
        print(
            f"{'3. +주체 @' + format(thr, '.2f'):<16}{r.ari:>9.4f}{r.pairwise.f1:>9.4f}"
            f"{r.n_pred_clusters:>6}{len(r.overmerges):>9}{len(r.oversplits):>9}{tag}"
        )

    print(
        f"\n최고: 2.+주체 @{args.threshold} ARI {results['2. +주체'].ari:.4f} / "
        f"3.완화 최고 @{best[0]:.2f} ARI {best[1]:.4f}"
    )

    # 최종(주체·완화 최고)의 남은 오류 사례
    final_r = best[2]
    print(
        f"\n[3.완화 @{best[0]:.2f}] 남은 잘못 합침 {len(final_r.overmerges)} · "
        f"잘못 나뉨 {len(final_r.oversplits)}"
    )
    for om in final_r.overmerges:
        print("  합침:", json.dumps(om.__dict__, ensure_ascii=False, default=str)[:200])
    for os_ in final_r.oversplits:
        print("  나뉨:", json.dumps(os_.__dict__, ensure_ascii=False, default=str)[:220])


if __name__ == "__main__":
    main()
