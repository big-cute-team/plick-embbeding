# Phase 02 — PoC 이관 + 재현

## 목표

plick-ai/poc-embedding의 파이프라인(임베딩 → 24h 롤링 윈도우 →
Agglomerative 군집화 → 리포트)이 이 리포에서 돌아가고, 기존 실험
(2026-06-29, published 56건, SEMANTIC_SIMILARITY@0.85 → 26이슈/중복묶음 15)
결과가 재현된다.

## 작업

- [ ] P02-T01 데이터 확보 — 기존 실험 입력(published 56건, title+summary_short)과
      기존 임베딩(tmp_embeddings)을 `data/` 스냅샷으로 고정
      (접근 정보는 개발자에게 요청 — Supabase 또는 plick-ai 리포의 results/)
- [ ] P02-T02 Gemini 임베딩 provider 구현 — gemini-embedding-001,
      task_type·차원 파라미터, 수동 L2 정규화, 로컬 캐시
- [ ] P02-T03 파이프라인 이관 — 24h 롤링 윈도우 후보 제한 + 전역
      Agglomerative(cosine, average linkage) + 임계 파라미터
- [ ] P02-T04 리포트 생성 — 군집 멤버·분포를 `results/<타임스탬프>/`에 저장,
      Confluence 실험 기록 템플릿 형식의 텍스트 출력
- [ ] P02-T05 재현 실행 — 기존 실험과 동일 조건으로 돌려 군집 결과 비교·기록

## 변경 범위

`src/plick_embedding/`, `scripts/`, `data/`, `tests/`, `docs/PROGRESS.md`,
`docs/DECISIONS.md`

## 완료 조건

- [ ] `scripts/run_experiment.py`가 (모델, task_type, 차원, 임계, 윈도우)
      파라미터로 실행되어 `results/<타임스탬프>/`에 config+report를 남긴다
- [ ] 캐시가 있으면 임베딩 API를 호출하지 않고 같은 결과를 낸다
- [ ] 기존 실험(SEMANTIC@0.85, 56건)과 같은 조건 실행 시 군집 수·중복묶음
      수가 기존 기록(26/15)과 일치하거나, 차이가 나면 원인이 리포트에 기록된다
- [ ] 파이프라인 단위 테스트(윈도우 제한·군집화)가 API 없이 통과한다

## 개발자 테스트

- [ ] `uv run python scripts/run_experiment.py --model gemini --task-type SEMANTIC_SIMILARITY --dim 768 --threshold 0.85 --window 24h` 실행 후 `results/` 최신 폴더의 report 확인
- [ ] report의 군집 결과를 Confluence 기록(페이지 15958018)과 눈으로 대조
