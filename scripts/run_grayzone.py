"""애매한 구간 LLM 판정 실험 — 순차 묶기(첫 기사) 기준선에 LLM 판정을 얹어 채점.

애매한 구간[gray-low, gray-high]에 걸린 쌍만 OpenAI에 "같은 사건인가?"를 물어
붙일지 정한다. 기준선(seed) 대비 잘못 합침·나뉨 변화, ARI, LLM 호출 수를 보여준다.

임베딩은 캐시라 비용 0이지만, **LLM 판정은 실제 API 호출**이다(첫 실행만, 이후 캐시).
먼저 --dry-run으로 호출 수만 확인하고, 실제 호출은 그다음에.

예: uv run python scripts/run_grayzone.py --dry-run
    uv run python scripts/run_grayzone.py            # 실제 LLM 호출
"""

import argparse
from datetime import timedelta
from pathlib import Path

from plick_embedding.eval.labels import load_labels
from plick_embedding.eval.scoring import ScoreResult
from plick_embedding.eval.scoring import score as score_clusters
from plick_embedding.judge import DEFAULT_JUDGE_MODEL, OpenAIJudge
from plick_embedding.pipeline.articles import load_articles
from plick_embedding.pipeline.gray_zone import cluster_with_gray_zone_judge
from plick_embedding.pipeline.incremental import cluster_incrementally
from plick_embedding.providers.base import EmbeddingConfig
from plick_embedding.providers.gemini import GeminiEmbeddingProvider
from plick_embedding.settings import PROJECT_ROOT, load_settings


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="애매한 구간 LLM 판정 묶기 (Gemini 선정 구성 기본)")
    p.add_argument("--task-type", default="SEMANTIC_SIMILARITY")
    p.add_argument("--dim", type=int, default=768)
    p.add_argument("--threshold", type=float, default=0.86)
    p.add_argument("--window", type=float, default=24.0)
    p.add_argument("--gray-low", type=float, default=0.80)
    p.add_argument("--gray-high", type=float, default=0.90)
    p.add_argument("--judge-model", default=DEFAULT_JUDGE_MODEL)
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="LLM을 부르지 않고 애매 구간 판정이 몇 건인지만 센다(항상 '예' 스텁)",
    )
    p.add_argument("--input", type=Path, default=PROJECT_ROOT / "data" / "articles.json")
    p.add_argument(
        "--labels", type=Path, default=PROJECT_ROOT / "data" / "labels" / "articles90.json"
    )
    return p


def _row(name: str, s: ScoreResult) -> str:
    return (
        f"| {name} | {s.n_pred_clusters} | {s.ari:.4f} | {s.pairwise.f1:.4f} | "
        f"{len(s.overmerges)} | {len(s.oversplits)} |"
    )


def _overmerge_issues(s: ScoreResult) -> set[str]:
    return {" + ".join(c.members_by_issue) for c in s.overmerges}


def main() -> None:
    args = build_parser().parse_args()
    settings = load_settings()
    if not settings.has_gemini:
        raise SystemExit("GEMINI_API_KEY가 없습니다 (.env 확인) — 임베딩은 캐시라도 키 확인용.")
    if not args.dry_run and not settings.has_openai:
        raise SystemExit("OPENAI_API_KEY가 없습니다 (.env 확인) — LLM 판정에 필요.")

    articles = load_articles(args.input)
    labels = load_labels(args.labels)
    window = timedelta(hours=args.window)
    texts = [a.embed_text for a in articles]
    published = [a.published_at for a in articles]

    cfg = EmbeddingConfig(model="gemini-embedding-001", task_type=args.task_type, dim=args.dim)
    provider = GeminiEmbeddingProvider(cfg, api_key=settings.gemini_api_key)
    emb = provider.embed(texts)

    # 기준선: 순차 묶기(첫 기사)
    base = cluster_incrementally(
        emb, published, threshold=args.threshold, window=window, representative="seed"
    )
    s_base = score_clusters(articles, base, labels)

    if args.dry_run:
        _, n_calls = cluster_with_gray_zone_judge(
            emb,
            published,
            texts,
            args.threshold,
            window,
            args.gray_low,
            args.gray_high,
            judge=lambda a, b: True,
        )
        print(f"\n[DRY RUN] 애매 구간 [{args.gray_low}, {args.gray_high}] 판정 대상 = {n_calls}건")
        print("  실제 LLM 호출 없음. 이 수만큼 OpenAI를 부르게 된다.\n")
        return

    judge = OpenAIJudge(api_key=settings.openai_api_key, model=args.judge_model)
    gz, n_calls = cluster_with_gray_zone_judge(
        emb, published, texts, args.threshold, window, args.gray_low, args.gray_high, judge=judge
    )
    s_gz = score_clusters(articles, gz, labels)

    print(
        f"\n기사 {len(articles)}건 · 기준값 {args.threshold} · 애매 구간 "
        f"[{args.gray_low}, {args.gray_high}] · 판정 모델 {args.judge_model}\n"
    )
    print("| 방식 | 묶음 수 | ARI | F1 | 잘못 합침 | 잘못 나뉨 |")
    print("|------|--------|-----|-----|----------|----------|")
    print(_row("순차(첫 기사)", s_base))
    print(_row("+ 애매구간 LLM", s_gz))
    print(f"\n애매 구간 판정 {n_calls}건 · 실제 LLM 호출 {judge.api_calls}건(나머지는 캐시)\n")

    print("== 잘못 합침 변화 ==")
    print(f"  기준선 {len(s_base.overmerges)}건 → LLM {len(s_gz.overmerges)}건")
    fixed = _overmerge_issues(s_base) - _overmerge_issues(s_gz)
    added = _overmerge_issues(s_gz) - _overmerge_issues(s_base)
    for m in sorted(fixed):
        print(f"  [막음] {m}")
    for m in sorted(added):
        print(f"  [새로 생김] {m}")


if __name__ == "__main__":
    main()
