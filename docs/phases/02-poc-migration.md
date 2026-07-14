# Phase 02 — PoC 이관 + 재현

## 목표

plick-ai/poc-embedding의 파이프라인(임베딩 → 24h 롤링 윈도우 →
병합형 군집화(Agglomerative) → 리포트)이 이 리포에서 돌아가고, 기존 실험
(2026-06-29, published 56건, SEMANTIC_SIMILARITY@0.85 → 26이슈/중복묶음 15)
결과가 재현된다.

## 작업

- [ ] P02-T01 실험 데이터 가져오기 — 예전 실험에 쓴 기사 56건(제목+짧은
      요약)과 그때 만들어 둔 임베딩 벡터(tmp_embeddings)를 받아서 `data/`에
      복사해 두고 다시는 안 바뀌게 고정한다
      (어디서 받는지는 개발자에게 요청 — Supabase 또는 plick-ai 리포)
- [ ] P02-T02 Gemini 임베딩 기능 만들기 — 기사 텍스트를 벡터로 바꾸는
      모듈(gemini-embedding-001). 용도 설정(task_type)과 벡터 크기(차원)를
      옵션으로 받고, 벡터 길이를 1로 맞추는 정규화(L2)를 직접 수행하고,
      같은 텍스트는 API를 다시 부르지 않게 로컬에 캐시한다
- [ ] P02-T03 묶기 로직 옮겨오기 — 최근 24시간 안의 기사만 비교 대상으로
      좁힌 뒤(롤링 윈도우), 비슷한 것끼리 차례로 합쳐가는 병합형
      군집화(cosine 유사도, average linkage)로 묶는다. "얼마나 비슷해야
      같은 이슈로 볼지" 기준값(임계값)은 옵션으로 받는다
- [ ] P02-T04 결과 리포트 만들기 — 어떤 기사끼리 묶였는지와 묶음 분포를
      `results/<타임스탬프>/`에 저장하고, Confluence 실험 기록 양식에 맞는
      텍스트로도 출력한다
- [ ] P02-T05 예전 실험 다시 돌려보기 — 예전과 똑같은 조건으로 실행해서
      같은 결과(이슈 26개/중복 묶음 15개)가 나오는지 비교하고 기록한다

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
