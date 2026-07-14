# CONVENTIONS

## 커밋

- 형식: `<type>(phase-NN): <요약>` — 예: `feat(phase-03): 주문 취소 API 추가`
- type: `feat` / `fix` / `refactor` / `test` / `docs` / `chore`
- phase 밖의 잡무(설정 등)는 `chore: <요약>`
- 하나의 커밋은 하나의 논리적 변경. phase 완료 시점에는 반드시 커밋이 존재해야 한다.

## 코드 스타일

- Python 3.12, uv 관리. 린트·포맷은 ruff 하나로 통일 (`ruff check` + `ruff format`).
- 네이밍: 모듈·함수·변수 `snake_case`, 클래스 `PascalCase`, 상수 `UPPER_SNAKE`.
- 공개 함수에는 타입 힌트를 붙인다. 설정·실험 파라미터는 dataclass로 묶는다.
- API 키는 `.env`(`GEMINI_API_KEY`, `OPENAI_API_KEY`)로만 주입. 코드·커밋에
  키를 넣지 않는다.
- 외부 API 호출은 재시도(지수 백오프) + 부분 실패 시 캐시로 재개 가능하게.
- 테스트: pytest, `tests/`에 소스 구조를 미러링. 외부 API는 목/캐시로 대체하고
  네트워크 없는 환경에서도 전체 테스트가 통과해야 한다.

## 실험 재현성 (이 리포의 핵심 규칙)

- 실행 1회 = `results/<타임스탬프>/` 하나. config(모델·task_type·차원·임계·
  윈도우·입력 데이터)와 result·report를 함께 저장한다.
- 같은 (텍스트 × 모델 × task_type × 차원) 임베딩은 캐시에서 재사용 —
  같은 입력으로 API를 두 번 호출하지 않는다.
- 랜덤성이 있는 단계는 시드를 고정한다.

## 실험 기록 (LLM Wiki)

- **1차 기록은 `wiki/`(Obsidian vault)** — 실험 1회 = `wiki/experiments/`에
  노트 1개 (`YYYY-MM-DD_HHMM_요약.md`), report 모듈이 자동 생성한다.
  frontmatter(model, task_type, dim, threshold, ari 등)를 채워 조회 가능하게.
- 실험에서 얻은 지식(모델 특성, 임계 감각, 엣지 케이스)은
  `wiki/models/`·`wiki/concepts/` 노트에 누적하고 `[[링크]]`로 연결한다.
- 노트를 수동으로 고쳐도 되지만 frontmatter의 조건·점수는 실행 결과와
  다르게 바꾸지 않는다 (재현성).
- 팀 차원 공유가 필요한 실험(구성 선정 등)은 Confluence "실험 기록
  (임베딩·중복처리)" 폴더에 요약 페이지로 올린다 — 제목·템플릿은 실험 기록
  가이드(페이지 14614543)를 따른다.

## 문서

- 프로젝트 상태 변경은 반드시 `docs/PROGRESS.md`에 반영한다.
- 스펙 밖 설계 결정은 `docs/DECISIONS.md`에 한 줄 추가한다.
- 문서는 짧게 유지한다. 오래된 내용은 남겨두지 말고 지운다 —
  git 히스토리가 과거를 기억한다.

