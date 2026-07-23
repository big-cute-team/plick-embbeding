"""전체 처리 흐름 실행 CLI — 가져오기 → 벡터 → 저장 → 묶기 → 어느 이슈인지 적기 (P08-T03).

배치·하나씩 러너와 짝. 이건 저장소(로컬 파일)에 벡터를 쌓아 두고, 다시 실행하면
이미 처리한 기사는 건너뛴다(두 번 돌려도 결과 같음). 기본 입력은 스냅샷
(data/articles.json)이라 인터넷 없이도 캐시된 벡터로 돌릴 수 있다.

예: uv run python scripts/run_pipeline.py \\
        --model gemini --task-type SEMANTIC_SIMILARITY --dim 768 \\
        --threshold 0.86 --window 24h
"""

import argparse
import sys
from datetime import timedelta
from pathlib import Path

from plick_embedding.pipeline.articles import load_articles
from plick_embedding.pipeline.batch import run_pipeline
from plick_embedding.pipeline.incremental import REPRESENTATIVES
from plick_embedding.pipeline.store import VectorStore
from plick_embedding.providers.base import EmbeddingConfig
from plick_embedding.providers.gemini import GeminiEmbeddingProvider
from plick_embedding.providers.openai import OpenAIEmbeddingProvider
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run_pipeline",
        description="PLick 전체 처리 흐름 (가져오기→벡터→저장→묶기→이슈 적기)",
    )
    parser.add_argument("--model", choices=sorted(MODEL_NAMES), default="gemini")
    parser.add_argument("--task-type", default="SEMANTIC_SIMILARITY")
    parser.add_argument("--dim", type=int, default=768)
    parser.add_argument("--threshold", type=float, default=0.86)
    parser.add_argument("--window", type=parse_window, default=timedelta(hours=24), metavar="24h")
    parser.add_argument("--representative", choices=REPRESENTATIVES, default="seed")
    parser.add_argument(
        "--input",
        type=Path,
        default=PROJECT_ROOT / "data" / "articles.json",
        help="기사 스냅샷 JSON (기본: data/articles.json)",
    )
    parser.add_argument(
        "--store",
        type=Path,
        default=PROJECT_ROOT / ".store" / "vectors.jsonl",
        help="벡터 저장 파일 (기본: .store/vectors.jsonl)",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = load_settings()

    if not args.input.exists():
        sys.exit(f"입력 파일이 없습니다: {args.input}")
    is_openai = args.model in OPENAI_MODELS
    if is_openai and not settings.has_openai:
        sys.exit("OPENAI_API_KEY가 없습니다. .env를 확인하세요 (.env.example 참고).")
    if not is_openai and not settings.has_gemini:
        sys.exit("GEMINI_API_KEY가 없습니다. .env를 확인하세요 (.env.example 참고).")

    articles = load_articles(args.input)
    task_type = "none" if is_openai else args.task_type
    config = EmbeddingConfig(model=MODEL_NAMES[args.model], task_type=task_type, dim=args.dim)
    if is_openai:
        provider = OpenAIEmbeddingProvider(config, api_key=settings.openai_api_key)
    else:
        provider = GeminiEmbeddingProvider(config, api_key=settings.gemini_api_key)

    store = VectorStore(args.store)
    before = len(store.known_ids())
    result = run_pipeline(
        articles,
        provider,
        store,
        threshold=args.threshold,
        window=args.window,
        representative=args.representative,
    )

    print(f"입력 {len(articles)}건 · 저장소 기존 {before}건")
    print(f"새로 처리: {result.new_count}건 → 저장소 총 {result.total}건")
    print(f"묶인 이슈: {result.issue_count}개")
    print(f"저장 파일: {args.store}")


if __name__ == "__main__":
    main()
