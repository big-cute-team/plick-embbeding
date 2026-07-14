# PROGRESS

> 프로젝트 상태의 단일 소스. 모든 세션은 이 파일을 읽고 시작하고,
> 이 파일을 갱신하고 끝난다. 형식(섹션 이름, Status 값)을 바꾸지 말 것.

## Current Phase

02 — PoC 이관 + 재현 (`docs/phases/02-poc-migration.md`)

## Current Task

P02-T01

## Status

NOT STARTED

## Completed

- [x] Phase 01 — 프로젝트 뼈대
- [ ] Phase 02 — PoC 이관 + 재현
- [ ] Phase 03 — 정답 라벨 + 정량 평가 러너
- [ ] Phase 04 — LLM Wiki (Obsidian) 구축
- [ ] Phase 05 — 모델별 task_type 실험 (2인 병렬: Gemini / OpenAI)
- [ ] Phase 06 — 결과 종합 · 최적 구성 선정
- [ ] Phase 07 — 증분 중복 묶기 + 예외 케이스
- [ ] Phase 08 — 수집→임베딩→벡터 저장 파이프라인

## Working Notes

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

none

## Developer Test

none
