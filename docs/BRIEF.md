# PROJECT_BRIEF

> 2026-07-14 init-project 초기화 입력 문서. PLick Confluence 문서
> (마스터 설계 9175112, 멘토링 적용 12943418, [Research] 임베딩 13860890,
> 중복 처리 파이프라인 15171586, 실험 기록 폴더 14843913)와
> 사용자 답변을 바탕으로 작성됨.

## 프로젝트 이름

plick-embedding (리포명: plick-embbeding)

## 한 줄 설명

PLick의 "같은 이슈 묶기(원문 N : 요약 1)"를 위한 임베딩 모델 벤치마크·실험 리포.
최적 모델 선정 후 수집→임베딩→벡터 저장 파이프라인까지 검증한다.

## 해결하려는 문제 / 목표

여러 기자가 같은 이적 이슈를 보도하면 원문 N개를 요약 1개로 묶어 품질을
올려야 한다(PLick v2 의미적 중복). 임베딩 유사도로 1차 판단하고 회색지대만
LLM에 맡기는 구조가 멘토링으로 확정됐고, 기존 PoC(plick-ai/poc-embedding)로
잠정 구성(gemini-embedding-001 · SEMANTIC_SIMILARITY · 768d · 임계 0.85 ·
24h 롤링 윈도우)까지 나왔다. 이 리포는 그 실험을 이어받아:

1. **임베딩 모델별(Google Gemini API vs OpenAI Embeddings API) ×
   task_type별 성능을 정량 비교**해 우리 서비스에 가장 좋은 구성을 선정한다.
2. 선정된 구성으로 **데이터 수집→임베딩→벡터 저장→증분 중복 묶기 처리**
   파이프라인을 만든다.
3. 검증된 결과는 최종적으로 plick-ai(FastAPI)로 이식한다.

## 핵심 기능

1. 기존 PoC 파이프라인 이관·재현 (임베딩 → 24h 윈도우 → 병합형 군집화 → 리포트)
2. 정답 라벨 + 정량 지표(ARI 등) 평가 러너 — "눈 검증"을 정량화
3. Gemini vs OpenAI 임베딩 모델 벤치마크 (모델 × task_type × 차원 × 임계)
4. 증분 중복 묶기 (발행 시각 순, 24h 활성 이슈와 비교) + 예외 케이스
   (오병합·여러 날 이어지는 이슈의 분할(사가 분할)) 검증, 회색지대 LLM 검수 실험
5. 선정 모델 기반 수집→임베딩→벡터 저장 파이프라인

## 제외 범위 (만들지 않을 것)

- FastAPI 등 HTTP 서버 — 실험·배치 리포. 서비스화는 plick-ai 합류로 결정
- LLM 요약 재생성(티어 결정 트리 실행) — plick-ai 영역. 여기서는 "같은 이슈 판단"까지
- 개인화 추천 (자문 3 영역)
- 운영 MySQL 스키마 쓰기 — 데이터는 읽기 전용, 산출물은 로컬/전용 저장소
- 자체 임베딩 모델 학습·파인튜닝 — API 기반(Gemini·OpenAI)만 비교
- 어드민 UI

## 기술 스택

Python 3.12 + uv, numpy/scikit-learn(군집화·지표), google-genai·openai SDK,
pytest·ruff. 서버 프레임워크 없음(CLI 스크립트). 벡터 저장은 수집 파이프라인
phase에서 Research 후 결정(로컬/MySQL vs 벡터DB).

> **추기 (2026-07-14, 초기화 직후 재설계)**: 2인 협업 방식 반영 —
> 벤치마크를 "Wiki 구축(04) → 2인 병렬 실험(05, 각자 Gemini/OpenAI 담당)
> → 결과 종합·선정(06)"으로 분해하고, 실험 기록 1차 저장소로 리포 내
> Obsidian 보관함(`wiki/`)을 도입했다. 상세는 docs/phases/와 DECISIONS.md.

## 제약 조건

- 임베딩 API 무료 티어/저비용 우선, 같은 텍스트 재호출 금지(캐시)
- 실험 기록 컨벤션 준수: 실험 1회 = Confluence 실험 기록 폴더에 페이지 1개
- 팀 컨벤션: 가공=Python, 파이프라인 저장 주체=admin-server(Node) 구조와 충돌 금지

## 참고 자료

- 마스터 설계: https://whoru3918.atlassian.net/wiki/spaces/P/pages/9175112
- 멘토링 적용(박동우): https://whoru3918.atlassian.net/wiki/spaces/P/pages/12943418
- [Research] 임베딩: https://whoru3918.atlassian.net/wiki/spaces/P/pages/13860890
- 중복 처리 파이프라인: https://whoru3918.atlassian.net/wiki/spaces/P/pages/15171586
- 실험 기록 폴더: https://whoru3918.atlassian.net/wiki/spaces/P/folder/14843913
- 기존 PoC 코드: plick-ai/poc-embedding/
