---
title: gemini-embedding-001
type: model
provider: Google (google-genai)
---

# gemini-embedding-001

Google의 임베딩 모델. 이 프로젝트의 트랙 A(Gemini)에서 쓰는 기본 모델.

## 특징

- **용도 설정([[task_type]])을 받는다** — 같은 텍스트라도 `SEMANTIC_SIMILARITY`,
  `CLUSTERING` 등 용도에 맞춰 벡터를 다르게 낸다. 우리는 주로
  `SEMANTIC_SIMILARITY`를 쓴다.
- **차원 선택** — 기본 768차원을 쓰고, 벡터 길이를 1로 맞추는 정규화(L2)를
  우리 코드에서 직접 한다.
- 같은 텍스트는 로컬 `.npy` 캐시로 재사용해 API를 다시 부르지 않는다.

## 실험 결과 (누적)

- [[2026-07-15_articles90_SEMANTIC_0.85_24h]] — 90건 기준선, ARI 0.9071 · F1 0.9091
- [[2026-06-29_published56_SEMANTIC_0.85_24h]] — 56건, 26이슈/묶음 15 (엣지 케이스 표출)
- [[2026-06-29_published56_CLUSTERING_0.92_24h]] — 56건, CLUSTERING과 비교
- 관찰: 명확한 단일 이적 사건은 임계 0.85로 정확. [[회색지대]]에서
  같은 팀·맥락의 다른 선수를 [[잘못 합침과 사가 분할|잘못 합침]] 하는 한계.

## 비교 대상

- [[text-embedding-3]] (트랙 B, OpenAI) — Phase 05에서 정량 비교.
