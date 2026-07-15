---
title: text-embedding-3
type: model
provider: OpenAI (openai)
---

# text-embedding-3

OpenAI의 임베딩 모델(text-embedding-3-small / -large). 이 프로젝트의
트랙 B(OpenAI)에서 쓸 모델. Phase 05에서 [[gemini-embedding-001]]과
정량 비교한다.

## 특징

- **용도 설정([[task_type]])이 없다** — Gemini와 달리 용도별 벡터 구분이
  없다. 대신 `dimensions` 파라미터로 벡터 차원을 줄일 수 있다(성능 대비 비용).
- small / large 두 크기. large가 정확하지만 느리고 비싸다.
- 벡터 길이를 1로 맞추는 정규화(L2)는 우리 코드에서 동일하게 적용한다.

## 실험 결과 (누적)

- 아직 없음 — Phase 05에서 90건 정답 라벨로 채점 예정
  ([[정답과 얼마나 일치하나 (ARI)]] · 묶음 정확도).

## 비교 관점

- Gemini는 용도 설정으로 "묶기"에 맞춰줄 수 있는 반면, OpenAI는 범용 벡터
  하나뿐 — 어느 쪽이 [[회색지대]] 구분을 잘하는지가 관전 포인트.
