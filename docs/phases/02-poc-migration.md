# Phase 02 — PoC 이관 + 기준선 확립

## 목표

plick-ai/poc-embedding의 파이프라인(임베딩 → 24h 롤링 윈도우 →
병합형 군집화(Agglomerative) → 리포트)이 이 리포에서 돌아가고,
새 데이터셋으로 잠정 구성(gemini-embedding-001 · SEMANTIC_SIMILARITY ·
768d · 임계 0.85 · 24h) 기준선 실험이 기록된다.

> 원래 목표였던 기존 실험(2026-06-29, published 56건 → 26이슈/중복묶음 15)
> 재현은 원본 데이터셋(기사 스냅샷·tmp_embeddings)이 소실되어 불가.
> 대신 새 데이터셋으로 기준선을 다시 세운다 (docs/DECISIONS.md 참조).

## 작업

- [ ] P02-T01 새 실험 데이터셋 구성 — 운영 데이터 소스에서 published 기사
      (제목+짧은 요약+발행시각)를 뽑아 `data/articles.json`으로 고정하고
      다시는 안 바뀌게 한다. 같은 이슈를 다룬 기사가 실제로 여럿 들어있는
      기간으로 고르고, 규모는 기존 실험과 비슷한 50~100건을 목표로 한다
- [x] P02-T02 Gemini 임베딩 기능 만들기 — 기사 텍스트를 벡터로 바꾸는
      모듈(gemini-embedding-001). 용도 설정(task_type)과 벡터 크기(차원)를
      옵션으로 받고, 벡터 길이를 1로 맞추는 정규화(L2)를 직접 수행하고,
      같은 텍스트는 API를 다시 부르지 않게 로컬에 캐시한다
- [x] P02-T03 묶기 로직 옮겨오기 — 최근 24시간 안의 기사만 비교 대상으로
      좁힌 뒤(롤링 윈도우), 비슷한 것끼리 차례로 합쳐가는 병합형
      군집화(cosine 유사도, average linkage)로 묶는다. "얼마나 비슷해야
      같은 이슈로 볼지" 기준값(임계값)은 옵션으로 받는다
- [x] P02-T04 결과 리포트 만들기 — 어떤 기사끼리 묶였는지와 묶음 분포를
      `results/<타임스탬프>/`에 저장하고, Confluence 실험 기록 양식에 맞는
      텍스트로도 출력한다
- [ ] P02-T05 기준선 실험 실행 — 새 데이터셋에 잠정 구성(SEMANTIC@0.85,
      768d, 24h)으로 실험을 돌려 결과를 남기고, 묶음 결과를 눈으로 검증해
      잘 묶인 것/오병합/놓친 것을 리포트에 기록한다. 이 결과가 이후
      phase(03 라벨, 05 벤치마크)의 비교 기준선이 된다

## 변경 범위

`src/plick_embedding/`, `scripts/`, `data/`, `tests/`, `docs/PROGRESS.md`,
`docs/DECISIONS.md`

## 완료 조건

- [ ] `scripts/run_experiment.py`가 (모델, task_type, 차원, 임계, 윈도우)
      파라미터로 실행되어 `results/<타임스탬프>/`에 config+report를 남긴다
- [ ] 캐시가 있으면 임베딩 API를 호출하지 않고 같은 결과를 낸다
- [ ] 새 데이터셋(`data/articles.json`)이 고정되고, 기준선 실험 1회의
      결과(묶음 수·눈 검증 코멘트)가 리포트에 기록된다
- [ ] 파이프라인 단위 테스트(윈도우 제한·군집화)가 API 없이 통과한다

## 개발자 테스트

- [ ] `uv run python scripts/run_experiment.py --model gemini --task-type SEMANTIC_SIMILARITY --dim 768 --threshold 0.85 --window 24h` 실행 후 `results/` 최신 폴더의 report 확인
- [ ] report의 묶음 결과를 눈으로 확인 (같은 이슈끼리 묶였는지)
