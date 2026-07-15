---
title: task_type
type: concept
---

# task_type (용도 설정)

임베딩을 "무슨 용도로 쓸지" 모델에 알려주는 설정. [[gemini-embedding-001]]은
같은 텍스트라도 용도에 따라 벡터를 다르게 낸다.

## 우리가 쓰는 값

- **SEMANTIC_SIMILARITY** — "두 글이 의미상 비슷한가"에 맞춘 벡터. 우리
  기준선이 쓰는 값. 명확한 같은 사건은 잘 붙는다.
- **CLUSTERING** — "여러 글을 무리로 묶기"에 맞춘 벡터. 임계값을 더 높게
  (예: 0.92) 잡아 쓴다.

## 실험에서 본 차이

- [[2026-06-29_published56_CLUSTERING_0.92_24h]] vs
  [[2026-06-29_published56_SEMANTIC_0.85_24h]]: 대부분 결과가 같았고,
  CLUSTERING@0.92가 약한 맥락 유사(제임스+라이스)를 덜 [[잘못 합침과 사가 분할|잘못 합침]] 하는
  미세한 차이. 결정적 차이는 아니었다.

## 참고

- [[text-embedding-3]]에는 task_type이 없다 — 범용 벡터 하나뿐.
- Phase 05에서 모델별로 task_type을 바꿔가며 비교하는 게 핵심 실험 축.
