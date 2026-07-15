---
model: text-embedding-3-large
task_type: none
input_text: title_short
dim: 1536
threshold: 0.58
window_hours: 24
dataset: articles90 (90건)
ari: 0.7568
pairwise_f1: 0.7619
date: 2026-07-15 14:49
author: 자동 생성
---

# 2026-07-15_articles90_oai-large-d1536_none_0.58_24h

> 실험 실행 시 자동 생성된 노트. `results/`는 git에 안 올라가므로
> 점수·대표 사례를 아래에 직접 담는다.

## 조건

| 항목 | 값 |
|------|-----|
| 모델 | text-embedding-3-large |
| task_type | none ([[task_type]]) |
| 입력 구성 | title_short |
| 차원 / 정규화 | 1536 / L2 |
| 임계값 | 0.58 |
| 비교 범위 | 최근 24시간만 비교 ([[최근 24시간만 비교]]) |
| 입력 데이터 | /Users/juns0720/project/Plick/plick-embbeding/data/articles.json (90건) |

## 결과

- 이슈(묶음) 수 / 중복 묶음 수: **59** / **13**
- 정답과 얼마나 일치하나 (ARI): **0.7568** ([[정답과 얼마나 일치하나 (ARI)]])
- 묶음 정확도(기사 쌍): 맞게 묶은 비율 0.8312 · 찾아낸 비율 0.7033 · 종합 0.7619

## 대표 사례

- 가장 큰 묶음 (8건): 맨유, 유리 틸레망스 영입 논의 중, 맨유, 유리 틸레만스 영입 협상 진행, 맨유, 유리 틸레망스 영입 임박
- [[잘못 합침과 사가 분할|잘못 합침]] 예: 예측 묶음 #5 = england_stop_haaland + guehi_haaland_training + haaland_england_wish
- [[잘못 합침과 사가 분할|잘못 나뉨]] 예: `alonso_chelsea_arrival`가 2개 묶음으로 나뉨

## 해석 · 다음 시도

- (해석을 채우세요)

## 참고

- 산출물: `/Users/juns0720/project/Plick/plick-embbeding/results/20260715_144918`
- 모델: [[text-embedding-3]]
