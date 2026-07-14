"""실험 실행 CLI 뼈대 — 실제 실험 로직은 Phase 02+에서 채운다."""

import argparse

from plick_embedding.settings import load_settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run_experiment",
        description="PLick 임베딩 벤치마크 실험 실행 (Gemini vs OpenAI)",
    )
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="현재 설정(API 키 존재 여부 등)을 출력하고 종료",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    settings = load_settings()
    print("현재 설정:")
    print(settings.summary())

    if args.show_config:
        return

    print("\n실험 로직은 아직 없습니다 (Phase 02+에서 구현). --help로 사용법을 확인하세요.")


if __name__ == "__main__":
    main()
