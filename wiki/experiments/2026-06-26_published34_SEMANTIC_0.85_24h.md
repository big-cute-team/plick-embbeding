---
model: gemini-embedding-001
task_type: SEMANTIC_SIMILARITY
dim: 768
threshold: 0.85
window_hours: 24
dataset: published34 (34건, 2026-06-23~06-25)
ari: null
pairwise_f1: null
date: 2026-06-26 14:23
author: 이민욱
---

# 2026-06-26_published34_SEMANTIC_0.85_24h

> Confluence 실험 기록에서 백필. 34건 소규모 데이터셋 초기 실험.
> 원본: [Confluence 15499266](https://whoru3918.atlassian.net/wiki/spaces/P/pages/15499266)

## 조건

| 항목 | 값 |
|------|-----|
| 모델 | gemini-embedding-001 |
| task_type | SEMANTIC_SIMILARITY ([[task_type]]) |
| 차원 / 정규화 | 768 / L2 |
| 임계값 | 0.85 |
| 비교 범위 | 최근 24시간만 비교 ([[최근 24시간만 비교]]) · 범위 밖 제외쌍 242 |
| 입력 데이터 | content_items published 34건 (2026-06-23~06-25), `tmp_embeddings` (이번에 새 글 15건 추가 임베딩) |

## 결과

- 총 **14개 이슈 / 중복 묶음 8개**.

## 대표 사례 · 해석

- 소규모(34건·짧은 기간)라 임계 0.85가 깔끔하게 동작 — 눈에 띄는
  [[잘못 합침과 사가 분할|잘못 합침]]·사가 분할이 거의 없었음.
- 같은 34건에서 CLUSTERING@0.92와 **멤버까지 완전히 동일**
  ([[2026-06-26_published34_CLUSTERING_0.92_24h]]) → 두 [[task_type]]이
  소규모에선 사실상 같은 결과.
- 한계는 데이터를 56건·여러 날로 늘린
  [[2026-06-29_published56_SEMANTIC_0.85_24h]]에서 드러남.

## 참고

- 모델: [[gemini-embedding-001]]
