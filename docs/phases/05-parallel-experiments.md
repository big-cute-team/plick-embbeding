# Phase 05 — 모델별 task_type 실험 (2인 병렬)

## 목표

두 사람이 모델을 하나씩 맡아(트랙 A: Gemini, 트랙 B: OpenAI) task_type·
차원·임계 실험을 병렬로 진행하고, 모든 결과를 wiki에 기록한다. 트랙 간
비교가 가능하도록 같은 데이터셋·같은 지표(Phase 03)·같은 노트 템플릿
(Phase 04)을 쓴다.

> 두 트랙은 순서 없이 병렬 진행 가능. 단 공용 코드(`providers/` 인터페이스,
> 러너)는 이 phase 시작 전 상태를 기준으로 하고, 공용 코드 변경이 필요하면
> 상대 트랙과 조율 후 반영한다.

## 작업

**공통**

- [ ] P05-T01 실험 계획 합의 — 트랙별 실험 매트릭스(task_type × 차원 ×
      임계 스윕 범위)를 wiki에 계획 노트로 작성

**트랙 A — Gemini (gemini-embedding-001)**

- [ ] P05-T02 task_type별 실험 — SEMANTIC_SIMILARITY, CLUSTERING (+필요시
      RETRIEVAL 계열) × 768/1536 × 임계 스윕, 라벨 셋 채점
- [ ] P05-T03 트랙 A 결과 정리 — 최고 구성·유지 임계 구간 폭·비용을 wiki
      모델 노트에 누적 기록

**트랙 B — OpenAI (text-embedding-3)**

- [ ] P05-T04 OpenAI provider 구현 — text-embedding-3-small/large,
      dimensions 파라미터, 캐시 (task_type 개념 부재는 노트에 명시)
- [ ] P05-T05 모델·차원별 실험 — small/large × dimensions × 임계 스윕,
      라벨 셋 채점
- [ ] P05-T06 트랙 B 결과 정리 — 최고 구성·유지 임계 구간 폭·비용을 wiki
      모델 노트에 누적 기록

## 변경 범위

`src/plick_embedding/providers/`, `scripts/`, `tests/`, `wiki/`,
`docs/PROGRESS.md`, `docs/DECISIONS.md`
(공용 파이프라인·eval 코드는 조율 없이 변경 금지)

## 완료 조건

- [ ] 트랙별 실험 매트릭스 계획 노트가 wiki에 있다
- [ ] 트랙 A: task_type 2종 이상 × 임계 스윕 결과가 wiki 실험 노트로 존재
- [ ] 트랙 B: 모델 2종(small/large) × 임계 스윕 결과가 wiki 실험 노트로 존재
- [ ] 모든 실험 노트에 같은 지표(ARI·pairwise)가 기록되어 트랙 간 비교 가능
- [ ] 각 트랙의 요약(최고 구성·임계 구간 폭·비용)이 wiki 모델 노트에 있다

## 개발자 테스트

- [ ] wiki INDEX에서 두 트랙의 실험 노트가 조건별로 조회되는지 확인
- [ ] 트랙 A·B 요약 노트를 나란히 놓고 Phase 06(종합) 진행 가능한지 판단
