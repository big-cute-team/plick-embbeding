---
model: gemini-embedding-001
task_type: CLUSTERING
dim: 768
threshold: 0.92
window_hours: 24
dataset: published56 (56건, 2026-06-23~06-28)
ari: null
pairwise_f1: null
date: 2026-06-29 12:37
author: 이민욱
---

# 2026-06-29_published56_CLUSTERING_0.92_24h

> Confluence 실험 기록에서 백필. [[2026-06-29_published56_SEMANTIC_0.85_24h]]와
> 같은 데이터로 task_type만 바꾼 교차 비교.
> 원본: [Confluence 15958044](https://whoru3918.atlassian.net/wiki/spaces/P/pages/15958044)

## 조건

| 항목 | 값 |
|------|-----|
| 모델 | gemini-embedding-001 |
| task_type | CLUSTERING ([[task_type]]) |
| 차원 / 정규화 | 768 / L2 |
| 임계값 | 0.92 |
| 비교 범위 | 최근 24시간만 비교 ([[최근 24시간만 비교]]) · 범위 밖 제외쌍 1039 |
| 입력 데이터 | content_items published 56건 (2026-06-23~06-28), `tmp_embeddings`(CLUSTERING) |

## 결과

- 총 **27개 이슈 / 중복 묶음 14개**. SEMANTIC@0.85(26이슈)와 거의 같으나 1건 차이.

## 대표 사례

- 잘 묶인 것: 팔레스트라 첼시 6건, 앤더슨 사가 등 SEMANTIC과 대부분 동일.
- 개선점: **"제임스(월드컵 복귀)+라이스(32강 출전)" [[잘못 합침과 사가 분할|잘못 합침]]을 안 함**
  (각자 단독). CLUSTERING 임계가 더 높아 약한 맥락 유사를 안 붙인 효과.
- 남은 문제: "아스날 기마랑이스+토날리" [[잘못 합침과 사가 분할|잘못 합침]]은 **양쪽 모두 남음** —
  같은 팀·같은 포지션 영입설은 임계만으로 못 가름([[회색지대]]).
- [[잘못 합침과 사가 분할|잘못 나뉨]](사가 분할): 앤더슨·킨스키 분할은 SEMANTIC과 동일하게 발생.

## 해석 · 다음 시도

- 두 [[task_type]] 모두 같은 한계(맥락 잘못 합침·사가 분할). CLUSTERING@0.92가
  약한 잘못 합침을 미세하게 덜 하지만 **결정적 차이는 아님**.
- 운영 견고성(임계 마진)은 여전히 SEMANTIC이 유리 → 잠정 기준을
  SEMANTIC@0.85로 유지.
- 회색지대 잘못 합침은 임계·task_type만으로 못 가른다 → LLM 검수 필요 재확인.

## 참고

- 비교: [[2026-06-29_published56_SEMANTIC_0.85_24h]]
- 모델: [[gemini-embedding-001]]
