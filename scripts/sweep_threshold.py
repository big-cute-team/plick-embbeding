"""임계값 스윕 — 한 (모델×차원) 세트를 임베딩 1회로 만들고, 같은 이슈로 볼
기준값(임계값)을 훑어 정답 라벨 기준 최고 ARI 지점을 찾는다.

임베딩은 캐시로 한 번만 만들고, 임계값 훑기는 그 벡터로 군집화만 다시 하므로
API를 다시 부르지 않는다. 최고 ARI 지점만 results/ + wiki 노트로 남긴다.

예: uv run python scripts/sweep_threshold.py --model openai-small --dim 768
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

from plick_embedding.eval.labels import load_labels
from plick_embedding.eval.scoring import score as score_clusters
from plick_embedding.pipeline.articles import EMBED_TEXT_MODES, embed_texts, load_articles
from plick_embedding.pipeline.clustering import cluster_embeddings
from plick_embedding.pipeline.window import split_clusters_by_window
from plick_embedding.providers.base import EmbeddingConfig
from plick_embedding.providers.gemini import GeminiEmbeddingProvider
from plick_embedding.providers.openai import OpenAIEmbeddingProvider
from plick_embedding.report.report import ExperimentConfig, build_clusters, write_report
from plick_embedding.report.wiki import write_wiki_note
from plick_embedding.settings import PROJECT_ROOT, load_settings

MODEL_NAMES = {
    "gemini": "gemini-embedding-001",
    "openai-small": "text-embedding-3-small",
    "openai-large": "text-embedding-3-large",
}
OPENAI_MODELS = {"openai-small", "openai-large"}


def parse_window(value: str) -> timedelta:
    if not value.endswith("h"):
        raise argparse.ArgumentTypeError(f"비교 시간 범위는 '24h' 형식이어야 합니다: {value!r}")
    return timedelta(hours=float(value[:-1]))


def thresholds(start: float, stop: float, step: float) -> list[float]:
    """start~stop을 step 간격으로 (부동소수 오차 없이) 나열한다."""
    n = round((stop - start) / step)
    return [round(start + i * step, 4) for i in range(n + 1)]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sweep_threshold",
        description="한 (모델×차원) 세트의 임계값을 훑어 최고 ARI 지점을 찾는다",
    )
    parser.add_argument("--model", choices=sorted(MODEL_NAMES), default="openai-small")
    parser.add_argument("--task-type", default="SEMANTIC_SIMILARITY")
    parser.add_argument("--dim", type=int, default=768)
    parser.add_argument("--window", type=parse_window, default=timedelta(hours=24), metavar="24h")
    parser.add_argument("--input", type=str, default=str(PROJECT_ROOT / "data" / "articles.json"))
    parser.add_argument(
        "--labels", type=str, default=str(PROJECT_ROOT / "data" / "labels" / "articles90.json")
    )
    parser.add_argument("--start", type=float, default=0.30)
    parser.add_argument("--stop", type=float, default=0.65)
    parser.add_argument("--step", type=float, default=0.05)
    parser.add_argument(
        "--input-text",
        choices=sorted(EMBED_TEXT_MODES),
        default="title_short",
        help="임베딩 입력 구성 (기본: title_short = 제목+짧은요약)",
    )
    parser.add_argument(
        "--no-note",
        action="store_true",
        help="노트·results를 남기지 않고 스윕 표만 출력 (탐색용)",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = load_settings()

    input_path = Path(args.input)
    labels_path = Path(args.labels)
    if not input_path.exists():
        sys.exit(f"입력 파일이 없습니다: {input_path}")
    if not labels_path.exists():
        sys.exit(f"라벨 파일이 없습니다: {labels_path}")

    is_openai = args.model in OPENAI_MODELS
    if is_openai and not settings.has_openai:
        sys.exit("OPENAI_API_KEY가 없습니다. .env를 확인하세요.")
    if not is_openai and not settings.has_gemini:
        sys.exit("GEMINI_API_KEY가 없습니다. .env를 확인하세요.")

    articles = load_articles(input_path)
    label_set = load_labels(labels_path)
    published = [a.published_at for a in articles]
    print(f"기사 {len(articles)}건 로드: {input_path}")

    # 임베딩은 한 번만 (캐시). 이후 임계값 훑기는 이 벡터로 군집화만 다시 한다.
    task_type = "none" if is_openai else args.task_type
    embedding_config = EmbeddingConfig(
        model=MODEL_NAMES[args.model], task_type=task_type, dim=args.dim
    )
    if is_openai:
        provider = OpenAIEmbeddingProvider(embedding_config, api_key=settings.openai_api_key)
    else:
        provider = GeminiEmbeddingProvider(embedding_config, api_key=settings.gemini_api_key)
    embeddings = provider.embed(embed_texts(articles, args.input_text))
    print(
        f"임베딩 완료: {embeddings.shape} · 입력 {args.input_text} "
        "— 임계값 훑기는 API를 다시 안 부릅니다\n"
    )

    best_threshold = None
    best_score = None
    best_labels = None
    print(f"{'임계값':>6} | {'ARI':>7} | {'F1':>7} | 묶음 수 | 잘못합침 | 잘못나뉨")
    print("-" * 56)
    for t in thresholds(args.start, args.stop, args.step):
        labels = cluster_embeddings(embeddings, threshold=t)
        labels = split_clusters_by_window(labels, published, window=args.window)
        s = score_clusters(articles, labels, label_set)
        n_clusters = len(set(int(x) for x in labels))
        mark = ""
        if best_score is None or s.ari > best_score.ari:
            best_threshold, best_score, best_labels = t, s, labels
            mark = "  ← 최고"
        print(
            f"{t:>6.2f} | {s.ari:>7.4f} | {s.pairwise.f1:>7.4f} | {n_clusters:>6} | "
            f"{len(s.overmerges):>7} | {len(s.oversplits):>7}{mark}"
        )

    tail = (
        "탐색 모드(--no-note): 노트를 남기지 않습니다."
        if args.no_note
        else "이 지점만 노트로 남깁니다."
    )
    print(
        f"\n최고 ARI: {best_score.ari:.4f} @ 임계값 {best_threshold:.2f} "
        f"(F1 {best_score.pairwise.f1:.4f}) — {tail}"
    )
    if args.no_note:
        return

    config = ExperimentConfig(
        model=embedding_config.model,
        task_type=embedding_config.task_type,
        dim=embedding_config.dim,
        threshold=best_threshold,
        window_hours=args.window.total_seconds() / 3600,
        input_path=str(input_path),
        n_articles=len(articles),
        input_text=args.input_text,
    )
    run_at = datetime.now()
    run_dir = write_report(config, articles, best_labels, score=best_score, run_at=run_at)
    clusters = build_clusters(articles, best_labels)
    note_path = write_wiki_note(config, clusters, run_at, score=best_score, run_dir=run_dir)
    print(f"결과 저장: {run_dir}")
    print(f"위키 노트: {note_path}")


if __name__ == "__main__":
    main()
