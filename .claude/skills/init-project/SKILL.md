---
name: init-project
description: agentic-starter 템플릿으로 만든 리포를 실제 프로젝트로 초기화한다. PROJECT_BRIEF.md를 읽고 docs/(SPEC, ARCHITECTURE, CONVENTIONS, phases, PROGRESS)와 CLAUDE.md를 프로젝트에 맞게 생성/갱신한다. 사용자가 "프로젝트 세팅해줘", "초기화해줘", "이 브리프로 시작하자", "init" 이라고 하거나, CLAUDE.md에 미초기화 안내가 남아 있는 리포에서 작업을 시작할 때 사용한다.
---

# init-project

템플릿 리포를 실제 프로젝트로 초기화하는 일회성 스킬. 아래 단계를 순서대로 수행한다.

## 1. 브리프 읽기

`PROJECT_BRIEF.md`를 읽는다.

- 파일이 없거나 사실상 비어 있으면: 사용자에게 브리프 작성을 요청하고 **정지**한다.
- "추천해줘"라고 된 항목(주로 기술 스택)은 프로젝트 성격에 맞는 선택지를 제안한다.

## 2. 부족한 정보 질문

다음이 브리프에서 불명확하면 AskUserQuestion으로 묻는다 (한 번에 최대 4개, 최대 2회):

- 기술 스택 (미정이면 2~3개 선택지 제안)
- 제외 범위 (비어 있으면 흔한 과잉 구현 후보를 제시하고 제외 여부 확인)
- 첫 마일스톤 (MVP에서 가장 먼저 동작해야 하는 것)
- 프로젝트 구조: 단일 모듈인가, 멀티 모듈/MSA인가 (브리프로 판단이 서면 묻지 않는다)

## 3. 문서 생성

브리프와 답변을 바탕으로 다음을 채운다. 각 파일의 기존 템플릿 주석은 실제
내용으로 대체하고 주석은 제거한다.

1. **`docs/SPEC.md`** — 한 줄 정의 / 핵심 기능(우선순위 순) / 제외 범위 / 용어(있으면)
2. **`docs/ARCHITECTURE.md`** — 스택 / 디렉토리 구조 / 주요 컴포넌트 / 실행·테스트 명령
3. **`docs/CONVENTIONS.md`** — "코드 스타일" 섹션을 선택된 스택의 컨벤션으로 채움
   (네이밍, 파일 구조, 에러 처리, 테스트 규칙). 커밋 형식 섹션은 그대로 둔다.
4. **`docs/specs/`** — API·이벤트·데이터 모델이 있는 프로젝트면 해당 JSON DSL 파일의
   뼈대를 생성 (specs/README.md의 형식). 없으면 건너뛴다.
5. **`docs/areas/`** — **멀티 모듈/MSA 프로젝트일 때만** 생성. 영역(모듈/서비스)마다
   `docs/areas/<영역>.md` 하나씩: 담당 범위 / 주요 디렉토리 / 스택·컨벤션 차이 /
   관련 스펙 포인터. 이 디렉토리가 존재하면 세션 시작 메뉴에 영역 선택 층이
   자동으로 생긴다 (AGENT_GUIDE.md 참조). 단일 모듈이면 만들지 않는다.
   영역은 컨텍스트 로딩 단위일 뿐 진행선(Current Phase/Status)은 프로젝트에
   하나다 — phase 파일의 `변경 범위`에 관련 영역을 명시하도록 phase를 설계한다.
6. **`docs/phases/`** — phase 파일 3~7개 생성.
   - `docs/phases/README.md`의 템플릿을 따르고, 섹션 제목(`목표`, `작업`,
     `변경 범위`, `완료 조건`, `개발자 테스트`)을 글자 그대로 사용한다.
   - Phase 01은 항상 "빌드·실행 가능한 프로젝트 뼈대"로 시작한다.
   - 한 phase는 한 세션에 끝나는 크기. 작업 ID는 `PNN-TNN`.
   - `00-EXAMPLE.md`는 삭제한다.
7. **`docs/PROGRESS.md`** — 초기화:
   - Current Phase: `01 — <이름>` (파일명 명시)
   - Current Task: `P01-T01`
   - Status: `NOT STARTED`
   - Completed: 전체 phase 체크리스트 (모두 미체크)
   - Working Notes: "init-project로 초기화됨. Phase 01부터 시작." 등 1~2줄
   - Blockers: `none`, Developer Test: `none`
8. **`CLAUDE.md`** — 상단의 미초기화 안내 블록을 제거하고, "프로젝트" 섹션에
   한 줄 소개 / 스택 / 실행·테스트 명령을 채운다. 문서 지도를 실제 생성물에
   맞게 갱신한다: `docs/BRIEF.md` 행 추가, specs를 만들지 않았으면 specs 행
   제거, `docs/areas/`를 만들었으면 영역 행 추가. 인덱스는 얇게 유지한다.

## 4. 마무리

1. `PROJECT_BRIEF.md`를 `docs/BRIEF.md`로 이동한다 (원본 기록 보존).
2. `README.md`를 프로젝트 소개(이름 / 한 줄 설명 / 실행·테스트 명령)로
   교체한다. 스타터 사용법·구조도·설계 원칙 등 템플릿 내용은 제거한다.
3. `docs/DECISIONS.md`의 예시 주석을 제거한다.
4. `.gitignore`에 선택된 스택의 항목(빌드 산출물, 의존성 디렉토리 등)을 추가한다.
5. 생성된 구조를 요약해 보여주고, phase 목록에 대한 피드백을 받는다.
6. 사용자가 동의하면 초기 커밋: `chore: init-project로 프로젝트 초기화`

## 규칙

- 이 스킬은 **문서만** 만든다. 코드 구현은 Phase 01에서 시작한다 — 진행 방법은
  AGENT_GUIDE.md의 골든 루프를 따르며, phase 진행 스킬(agentic-phase-runner 등)이
  설치돼 있다면 그것을 써도 된다.
- PROGRESS.md의 섹션 이름과 Status 값(`NOT STARTED` / `IN PROGRESS` /
  `AWAITING REVIEW` / `DONE`)은 워크플로우 스킬들이 파싱한다 — 형식을 바꾸지 않는다.
- 브리프에 없는 내용을 상상으로 채우지 않는다. 불확실하면 묻거나 비워두고 표시한다.
