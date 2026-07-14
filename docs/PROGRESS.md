# PROGRESS

> 프로젝트 상태의 단일 소스. 모든 세션은 이 파일을 읽고 시작하고,
> 이 파일을 갱신하고 끝난다. 형식(섹션 이름, Status 값)을 바꾸지 말 것.

## Current Phase

02 — PoC 이관 + 기준선 확립 (`docs/phases/02-poc-migration.md`)

## Current Task

P02-T05

## Status

IN PROGRESS

## Completed

- [x] Phase 01 — 프로젝트 뼈대
- [ ] Phase 02 — PoC 이관 + 기준선 확립
- [ ] Phase 03 — 정답 라벨 + 정량 평가 러너
- [ ] Phase 04 — LLM Wiki (Obsidian) 구축
- [ ] Phase 05 — 모델별 task_type 실험 (2인 병렬: Gemini / OpenAI)
- [ ] Phase 06 — 결과 종합 · 최적 구성 선정
- [ ] Phase 07 — 증분 중복 묶기 + 예외 케이스
- [ ] Phase 08 — 수집→임베딩→벡터 저장 파이프라인

## Working Notes

- 2026-07-14 P02-T01 완료 — `.env.local`의 Supabase 접근 정보로
  article_summaries에서 PUBLISHED 기사 90건(published_at 2026-07-09~13 UTC)을
  추출해 `data/articles.json` 고정 (`scripts/fetch_articles.py`, 기존 파일
  덮어쓰기 거부). 파이프라인 로더로 로드 검증, 테스트 13개·ruff 통과.
  남은 것: T05 기준선 실험 — GEMINI_API_KEY가 `.env`에 없어 블록 (Blockers 참조).
- 2026-07-14 기존 데이터셋(기사 56건·tmp_embeddings) 소실 확인 → Phase 02를
  "재현"에서 "새 데이터셋 기준선 확립"으로 재구성 (phase 파일·DECISIONS 갱신).
  T01=새 스냅샷 고정, T05=잠정 구성 기준선 실험+눈 검증. T02~T04 코드는 그대로 유효.
- 2026-07-14 Phase 02 T02~T04 구현 완료 (트랙 A) — providers(base/cache/
  gemini: task_type·차원 옵션, L2 정규화, .npy 파일 캐시, 지수 백오프),
  pipeline(articles 로더·병합형 군집화·윈도우 분리), report(results/
  <타임스탬프>/ config+result+report.md). 테스트 13개(API 없이 통과).
  윈도우 적용 방식은 DECISIONS.md 참조 (T05에서 검증 필요).
- 남은 것: T01(데이터)·T05(재현) — 기사 56건+tmp_embeddings 접근 정보 필요.
  로컬 plick-ai/prototype 리포에는 poc-embedding 코드·데이터 없음 확인.
  입력 형식은 data/articles.json: [{id, title, summary_short, published_at}].
- 2026-07-14 Phase 01 완료 (트랙 A) — pyproject.toml(uv, Python 3.12),
  src/plick_embedding/{providers,pipeline,eval,report}, settings 모듈(.env 로드,
  키 값 비노출 summary), scripts/run_experiment.py 뼈대(--help/--show-config),
  테스트 3개·ruff 설정. `.gitignore`에 `!.env.example` 예외 추가
  (`.env.*` 규칙이 견본 파일까지 무시하던 문제). 완료 조건 4개 전부 통과.
  다음 세션 참고: Phase 02는 기존 실험 데이터(published 56건·tmp_embeddings)
  접근 정보가 필요 — 개발자 제공 대기.
- 2026-07-14 init-project로 초기화됨 (Confluence 설계·실험 문서 분석 기반).
  Phase 01부터 시작.
- 2026-07-14 문서 전체 용어 정리 — dedup→중복 묶기, Agglomerative→병합형
  군집화, vault→보관함 등 (가독성).
- 2026-07-14 Phase 01~04 병렬 트랙 확정 — 트랙 A(개발: 01→02→03 러너) /
  트랙 B(지식·라벨: 04 보관함·노트 → 03 라벨). 티켓 6장 분리안은
  `docs/phases/README.md`의 "병렬 진행 가이드" 참조.
- 2026-07-14 Confluence 마스터 문서(9175112) 반영용 초안 작성 —
  `docs/CONFLUENCE_UPDATE.md` (연결 복구 후 게시).
- 2026-07-14 phase 01~08 작업(태스크) 설명을 쉬운 문장으로 전면 재작성
  (가독성 — 작업 ID·체크박스·완료 조건은 그대로).
- Phase 02 착수 전 필요: 기존 실험 데이터(published 56건·tmp_embeddings)
  접근 정보 — 개발자 제공 대기.

## Blockers

- P02-T05: `GEMINI_API_KEY`가 없어 기준선 실험 실행 불가 — 프로젝트 루트
  `.env`에 키를 넣어주세요 (`.env.example` 참고). 키 제공 후 "진행" 지시.

## Developer Test

none
