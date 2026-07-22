"""하나씩 묶기 실험 실행 CLI — 임베딩 → 발행 시각 순으로 한 건씩 묶기 → 리포트.

배치 러너(run_experiment.py)와 짝. 전체를 한 번에 묶는 대신, 새 기사가 하나씩
들어오는 운영 상황을 흉내 내 발행 시각 순으로 한 건씩 처리한다.

예: uv run python scripts/run_incremental.py \\
        --model gemini --task-type SEMANTIC_SIMILARITY \\
        --dim 768 --threshold 0.86 --window 24h --representative centroid \\
        --labels data/labels/articles90.json
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

from plick_embedding.eval.labels import load_labels
from plick_embedding.eval.scoring import score as score_clusters
from plick_embedding.pipeline.articles import load_articles
from plick_embedding.pipeline.incremental import REPRESENTATIVES, cluster_incrementally
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
    """ "24h" / "36h" 형식을 timedelta로 바꾼다."""
    if not value.endswith("h"):
        raise argparse.ArgumentTypeError(f"비교 시간 범위는 '24h' 형식이어야 합니다: {value!r}")
    return timedelta(hours=float(value[:-1]))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run_incremental",
        description="PLick 하나씩 묶기 실험 실행 (발행 시각 순 증분 처리)",
    )
    parser.add_argument("--model", choices=sorted(MODEL_NAMES), default="gemini")
    parser.add_argument("--task-type", default="SEMANTIC_SIMILARITY")
    parser.add_argument("--dim", type=int, default=768)
    parser.add_argument("--threshold", type=float, default=0.86)
    parser.add_argument(
        "--window",
        type=parse_window,
        default=timedelta(hours=24),
        metavar="24h",
        help="최근 몇 시간 안에 갱신된 묶음만 후보 (기본: 24h)",
    )
    parser.add_argument(
        "--representative",
        choices=REPRESENTATIVES,
        default="centroid",
        help="묶음 대표값 (centroid=평균 / latest=최신 기사 / seed=첫 기사, 기본: centroid)",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=PROJECT_ROOT / "data" / "articles.json",
        help="기사 스냅샷 JSON (기본: data/articles.json)",
    )
    parser.add_argument(
        "--labels",
        type=Path,
        default=None,
        help="정답 라벨 JSON. 있으면 리포트에 정량 점수 포함",
    )
    parser.add_argument(
        "--show-config", action="store_true", help="현재 설정(API 키 존재 여부 등)을 출력하고 종료"
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = load_settings()

    if args.show_config:
        print("현재 설정:")
        print(settings.summary())
        return

    if not args.input.exists():
        sys.exit(f"입력 파일이 없습니다: {args.input}")
    is_openai = args.model in OPENAI_MODELS
    if is_openai and not settings.has_openai:
        sys.exit("OPENAI_API_KEY가 없습니다. .env를 확인하세요 (.env.example 참고).")
    if not is_openai and not settings.has_gemini:
        sys.exit("GEMINI_API_KEY가 없습니다. .env를 확인하세요 (.env.example 참고).")

    articles = load_articles(args.input)
    print(f"기사 {len(articles)}건 로드: {args.input}")

    task_type = "none" if is_openai else args.task_type
    embedding_config = EmbeddingConfig(
        model=MODEL_NAMES[args.model], task_type=task_type, dim=args.dim
    )
    if is_openai:
        provider = OpenAIEmbeddingProvider(embedding_config, api_key=settings.openai_api_key)
    else:
        provider = GeminiEmbeddingProvider(embedding_config, api_key=settings.gemini_api_key)
    embeddings = provider.embed([a.embed_text for a in articles])
    print(f"임베딩 완료: {embeddings.shape}")

    labels = cluster_incrementally(
        embeddings,
        [a.published_at for a in articles],
        threshold=args.threshold,
        window=args.window,
        representative=args.representative,
    )

    score = None
    if args.labels is not None:
        if not args.labels.exists():
            sys.exit(f"라벨 파일이 없습니다: {args.labels}")
        label_set = load_labels(args.labels)
        missing = label_set.missing([a.id for a in articles])
        if missing:
            print(
                f"경고: 정답 라벨이 없는 기사 {len(missing)}건은 채점에서 제외합니다 "
                f"(예: {', '.join(missing[:5])}{' …' if len(missing) > 5 else ''})"
            )
        score = score_clusters(articles, labels, label_set)
        print(
            f"정량 평가: ARI {score.ari:.4f} · F1 {score.pairwise.f1:.4f} "
            f"(잘못 합침 {len(score.overmerges)}건 · 잘못 나뉨 {len(score.oversplits)}건)"
        )

    config = ExperimentConfig(
        model=embedding_config.model,
        task_type=embedding_config.task_type,
        dim=embedding_config.dim,
        threshold=args.threshold,
        window_hours=args.window.total_seconds() / 3600,
        input_path=str(args.input),
        n_articles=len(articles),
        mode="incremental",
        representative=args.representative,
    )
    run_at = datetime.now()
    run_dir = write_report(config, articles, labels, score=score, run_at=run_at)
    print(f"결과 저장: {run_dir}")

    clusters = build_clusters(articles, labels)
    note_path = write_wiki_note(config, clusters, run_at, score=score, run_dir=run_dir)
    print(f"위키 노트: {note_path}")

    print((run_dir / "report.md").read_text(encoding="utf-8").split("## 중복 묶음 상세")[0])


if __name__ == "__main__":
    main()
