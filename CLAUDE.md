# CLAUDE.md

이 파일은 얇은 인덱스다. 규칙 본문을 여기에 늘리지 말고 아래 문서에 둔다.

## 프로젝트

PLick의 "같은 이슈 묶기(원문 N:요약 1)"를 위한 임베딩 모델 벤치마크·실험
리포. Gemini vs OpenAI 임베딩을 정량 비교해 최적 구성을 선정하고,
수집→임베딩→벡터 저장→증분 dedup 파이프라인을 검증한다 (최종 이식처: plick-ai).

- 스택: Python 3.12 + uv, numpy/scikit-learn, google-genai·openai, pytest·ruff.
  서버 없음 — CLI 실험·배치 리포.
- 실행/테스트: `uv sync` · `uv run pytest` · `uv run ruff check .` ·
  `uv run python scripts/run_experiment.py --help`

## 문서 지도 — 필요할 때만 읽기

| 언제 | 무엇을 |
|------|--------|
| 세션 시작, 작업 착수 전 | `docs/PROGRESS.md` → 현재 phase 파일 (`docs/phases/`) |
| 행동 규칙이 궁금할 때 | `docs/AGENT_GUIDE.md` |
| 무엇을 만드는지 / 만들지 않는지 | `docs/SPEC.md` |
| 스택·구조·실행 명령 | `docs/ARCHITECTURE.md` |
| 코드 작성 전 (특히 실험 재현성 규칙) | `docs/CONVENTIONS.md` |
| 초기화 당시 배경·Confluence 정본 링크 | `docs/BRIEF.md` |
| 과거 실험 결과·모델 지식을 참고할 때 | `wiki/00-INDEX.md` (Obsidian vault) |
| 스펙 밖 결정을 내렸을 때 | `docs/DECISIONS.md`에 한 줄 기록 |

## 핵심 규칙 (항상 적용)

- 사용자가 구체적 지시 없이 세션을 여는 말("일어나", "시작하자", "뭐부터 할까"
  등 의도 기준)을 하면: `docs/AGENT_GUIDE.md`의 "세션 시작 메뉴" 절차에 따라
  `docs/PROGRESS.md`를 읽고 메뉴를 띄운다. 그 외 프로젝트 문서는 사용자가
  선택한 뒤에만 로드한다. 끝내려는 말("오늘 그만", "정리하자" 등)을 하면
  같은 문서의 "세션 마무리" 절차를 수행한다.
- 작업은 골든 루프를 따른다: PROGRESS 읽기 → 현재 phase 하나만 수행 →
  완료 조건 자가 점검 → PROGRESS 기록 → 정지. 상세는 `docs/AGENT_GUIDE.md`.
- 한 번에 한 phase. 다음 phase를 이어서 진행하지 않는다.
- phase 파일의 `변경 범위` 밖은 수정하지 않는다. SPEC의 제외 범위는 구현하지 않는다.
- `docs/` 전체를 한꺼번에 읽지 않는다. 위 지도 기준으로 필요한 것만 읽는다.
- 중요한 상태·결정은 대화에만 남기지 말고 해당 문서에 기록한다.
- 실험을 돌렸으면 결과를 `results/` + `wiki/experiments/` 노트로 남긴다.
  기록 규칙은 `docs/CONVENTIONS.md`의 "실험 기록 (LLM Wiki)" 절.
