---
model: gemini-embedding-001
task_type: CLUSTERING
dim: 768
threshold: 0.92
window_hours: 24
dataset: published34 (34건, 2026-06-23~06-25)
ari: null
pairwise_f1: null
date: 2026-06-26 14:30
author: 이민욱
---

# 2026-06-26_published34_CLUSTERING_0.92_24h

> Confluence 실험 기록에서 백필. [[2026-06-26_published34_SEMANTIC_0.85_24h]]와
> 같은 34건으로 task_type만 바꾼 교차 검증.
> 원본: [Confluence 15597570](https://whoru3918.atlassian.net/wiki/spaces/P/pages/15597570)

## 조건

| 항목 | 값 |
|------|-----|
| 모델 | gemini-embedding-001 |
| task_type | CLUSTERING ([[task_type]]) |
| 차원 / 정규화 | 768 / L2 |
| 임계값 | 0.92 |
| 비교 범위 | 최근 24시간만 비교 ([[최근 24시간만 비교]]) · 범위 밖 제외쌍 242 |
| 입력 데이터 | content_items published 34건 (2026-06-23~06-25), `tmp_embeddings`(CLUSTERING) |

## 결과

- 총 **14개 이슈 / 중복 묶음 8개** — SEMANTIC@0.85 결과와 **멤버까지 완전히 동일**.

## 해석

- 소규모(34건)에서는 [[task_type]] SEMANTIC vs CLUSTERING이 사실상 같은
  결과를 낸다는 교차 검증. 두 용도 설정의 차이는
  [[2026-06-29_published56_CLUSTERING_0.92_24h|56건 이상 규모]]에서야 미세하게
  드러났다.

## 참고

- 비교: [[2026-06-26_published34_SEMANTIC_0.85_24h]]
- 모델: [[gemini-embedding-001]]
