---
title: 트랙B_OpenAI_매트릭스
type: plan
phase: "05"
track: B
owner: 개발자(OpenAI)
---

# 트랙 B — OpenAI 실험 매트릭스

[[공통 실험 기준]]을 따르되, OpenAI([[text-embedding-3]]) 쪽 실험 조합을
독립 설계한다. 트랙 A(Gemini)와 무관하게 진행.

## 고정 조건 (공통)

- 데이터셋 articles90(90건) · 정답 라벨 56이슈 · 비교 범위 최근 24시간만 비교
- 입력 텍스트: 제목+짧은요약 (1차). 여력 되면 제목+상세요약 추가 비교.

## 바꿔볼 축

| 축 | 값 |
|----|-----|
| 모델 | text-embedding-3-**small** / text-embedding-3-**large** |
| 벡터 크기(dimensions) | 768 / 1536 (large는 3072도 선택) |
| 임계값 | 0.30 ~ 0.65를 0.05 간격으로 훑어 최고 ARI 지점 탐색 |

> OpenAI에는 [[task_type]]이 없다 — 범용 벡터 하나뿐이라 Gemini의 task_type
> 축이 없다. 대신 모델 크기(small/large)와 차원이 주요 축.

## 임베딩 실행 = 4세트 (임계값은 재임베딩 불필요)

임계값 훑기는 이미 만든 벡터로 군집화만 다시 하므로 API를 다시 안 부른다.
따라서 실제 임베딩 호출은 아래 4세트뿐:

| # | 모델 | 차원 | 명령 |
|---|------|------|------|
| 1 | small | 768 | `--model openai-small --dim 768` |
| 2 | small | 1536 | `--model openai-small --dim 1536` |
| 3 | large | 768 | `--model openai-large --dim 768` |
| 4 | large | 1536 | `--model openai-large --dim 1536` |

각 세트마다 임계값 0.30~0.65를 훑어 최고 ARI를 고른 뒤, 그 조건으로 실험
노트를 남긴다.

## 예상 비용 (참고)

- 90건 × 약 50토큰 ≈ 4,500토큰/세트 × 4세트 ≈ 18,000토큰.
- text-embedding-3-small $0.02 / 1M · large $0.13 / 1M → **총 약 $0.002(≈수 원)**.
- 캐시가 있으니 재실행은 무료.

## 산출물

- 세트별 실험 노트(experiments/) + [[text-embedding-3]] 모델 노트에 최고
  구성·임계 유지 구간 폭·비용 요약(T08).
