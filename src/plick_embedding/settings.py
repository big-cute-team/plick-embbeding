"""환경 설정 로드 — API 키는 .env로만 주입한다 (코드·커밋 금지)."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str | None
    openai_api_key: str | None

    @property
    def has_gemini(self) -> bool:
        return bool(self.gemini_api_key)

    @property
    def has_openai(self) -> bool:
        return bool(self.openai_api_key)

    def summary(self) -> str:
        """키 값은 노출하지 않고 설정 상태만 요약한다."""
        lines = [
            f"GEMINI_API_KEY: {'설정됨' if self.has_gemini else '없음'}",
            f"OPENAI_API_KEY: {'설정됨' if self.has_openai else '없음'}",
        ]
        return "\n".join(lines)


def load_settings(env_file: Path | None = None) -> Settings:
    """`.env`(기본: 프로젝트 루트)를 읽어 Settings를 만든다."""
    load_dotenv(env_file or PROJECT_ROOT / ".env")
    return Settings(
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )
