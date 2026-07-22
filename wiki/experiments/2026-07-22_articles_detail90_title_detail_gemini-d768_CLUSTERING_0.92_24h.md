---
model: gemini-embedding-001
task_type: CLUSTERING
input_text: title_detail
dim: 768
threshold: 0.92
window_hours: 24
dataset: articles_detail90 (90건)
ari: 0.8117
pairwise_f1: 0.8163
date: 2026-07-22 13:39
author: 자동 생성
---

# 2026-07-22_articles_detail90_title_detail_gemini-d768_CLUSTERING_0.92_24h

> 실험 실행 시 자동 생성된 노트. `results/`는 git에 안 올라가므로
> 점수·대표 사례를 아래에 직접 담는다.

## 조건

| 항목 | 값 |
|------|-----|
| 모델 | gemini-embedding-001 |
| task_type | CLUSTERING ([[task_type]]) |
| 입력 구성 | title_detail |
| 차원 / 정규화 | 768 / L2 |
| 임계값 | 0.92 |
| 비교 범위 | 최근 24시간만 비교 ([[최근 24시간만 비교]]) |
| 입력 데이터 | data/articles_detail.json (90건) |

## 결과

- 이슈(묶음) 수 / 중복 묶음 수: **55** / **15**
- 정답과 얼마나 일치하나 (ARI): **0.8117** ([[정답과 얼마나 일치하나 (ARI)]])
- 묶음 정확도(기사 쌍): 맞게 묶은 비율 0.7619 · 찾아낸 비율 0.8791 · 종합 0.8163

## 대표 사례

- 가장 큰 묶음 (11건): 맨유, 유리 틸레망스 영입 논의 중, 맨유, 유리 틸레만스 영입 협상 진행, 맨유, 유리 틸레망스 영입 임박
- [[잘못 합침과 사가 분할|잘못 합침]] 예: 예측 묶음 #1 = manutd_two_midfielders_85m + tielemans_manutd
- [[잘못 합침과 사가 분할|잘못 나뉨]] 예: `alonso_chelsea_arrival`가 2개 묶음으로 나뉨

## 해석 · 다음 시도

- (해석을 채우세요)

## 참고

- 산출물: `/Users/juns0720/project/Plick/plick-embbeding/results/20260722_133922`
- 모델: [[gemini-embedding-001]]
