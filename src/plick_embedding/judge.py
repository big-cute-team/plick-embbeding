"""애매한 구간 LLM 판정 — 두 기사가 같은 사건인지 예/아니오로 답한다.

임베딩 유사도가 애매한 구간(예: 0.80~0.90)에 걸린 쌍만 이 판정기에 물어본다.
판정 LLM은 OpenAI(생성·판정 스택)를 쓴다 — 임베딩만 Gemini(벤치마크 선정).
응답은 로컬 캐시에 저장해 같은 쌍을 두 번 호출하지 않는다(재실행은 비용 0).
"""

import hashlib
import time
from pathlib import Path

from plick_embedding.settings import PROJECT_ROOT

DEFAULT_JUDGE_CACHE_DIR = PROJECT_ROOT / ".cache" / "judge"
DEFAULT_JUDGE_MODEL = "gpt-4o-mini"
MAX_RETRIES = 4
BACKOFF_BASE_SECONDS = 2.0

PROMPT = """아래 "새 기사"가 "기존 묶음"과 같은 이슈(하나의 이어지는 사건)인지 판단해줘.

- 하나의 이슈는 같은 사건이 시간에 따라 전개되는 것을 모두 포함한다. 예를 들어 한 선수의
  한 이적 건은 협상 → 합의 → 메디컬 → 확정으로 단계가 이어져도 전부 같은 이슈다.
- 같은 선수·팀이 나와도 사건 자체가 다르면 "아니오"다. 예: 이적 기사 vs 대표팀 경기 기사,
  또는 서로 다른 이적 건.

반드시 "예" 또는 "아니오" 한 단어로만 답해.

[기존 묶음 — 이 묶음에 이미 속한 기사들]
{b}

[새 기사]
{a}

새 기사가 위 묶음과 같은 이슈인가? (예/아니오)"""


class JudgeCache:
    """(모델 × 기사쌍) → 판정 문자열. 파일 1개 = 판정 1개."""

    def __init__(self, cache_dir: Path = DEFAULT_JUDGE_CACHE_DIR) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, model: str, a: str, b: str) -> Path:
        key = f"{model}|{a}|{b}"
        return self.cache_dir / f"{hashlib.sha256(key.encode('utf-8')).hexdigest()}.txt"

    def get(self, model: str, a: str, b: str) -> str | None:
        path = self._path(model, a, b)
        return path.read_text(encoding="utf-8").strip() if path.exists() else None

    def put(self, model: str, a: str, b: str, verdict: str) -> None:
        self._path(model, a, b).write_text(verdict, encoding="utf-8")


def parse_verdict(text: str) -> bool:
    """LLM 응답을 '같은 사건인가'(True/False)로 해석한다. 애매하면 보수적으로 False."""
    t = text.strip().lower()
    return t.startswith("예") or t.startswith("yes")


class OpenAIJudge:
    """OpenAI로 두 기사가 같은 사건인지 판정한다. 캐시에 있으면 API를 부르지 않는다."""

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_JUDGE_MODEL,
        cache: JudgeCache | None = None,
    ) -> None:
        self._api_key = api_key
        self.model = model
        self._cache = cache or JudgeCache()
        self._client = None  # 캐시만으로 끝나면 클라이언트를 만들지 않는다
        self.api_calls = 0  # 실제 API 호출 수(캐시 적중은 제외) — 비용 측정용

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI(api_key=self._api_key)
        return self._client

    def __call__(self, a: str, b: str) -> bool:
        cached = self._cache.get(self.model, a, b)
        if cached is not None:
            return parse_verdict(cached)
        verdict = self._ask(PROMPT.format(a=a, b=b))
        self._cache.put(self.model, a, b, verdict)
        return parse_verdict(verdict)

    def _ask(self, prompt: str) -> str:
        client = self._get_client()
        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0,
                )
                self.api_calls += 1
                return (response.choices[0].message.content or "").strip()
            except Exception as error:  # noqa: BLE001 — SDK 예외 계층이 넓어 전부 재시도
                last_error = error
                if attempt < MAX_RETRIES - 1:
                    time.sleep(BACKOFF_BASE_SECONDS * (2**attempt))
        raise RuntimeError(f"OpenAI 판정 {MAX_RETRIES}회 재시도 실패") from last_error
