# plick-ai 이식 가이드 (P08-T05)

> 이 리포(plick-embbeding)에서 정량 실험으로 확정한 "같은 이슈 묶기" 구성과
> 파이프라인을 **plick-ai(AI 서버)로 옮기기 위한 안내서**다. 실제 이식 작업은
> plick-ai 리포에서 한다. 여기서는 무엇을·어떤 경계로 옮기고, 운영에서 무엇이
> 바뀌는지, 아직 안 정한 게 무엇인지를 적는다.
>
> 용어: **이슈** = 같은 사건을 다룬 원문 묶음(원문 N : 요약 1). **잘못 합침** =
> 다른 사건이 한 묶음에 섞임. **ARI** = 정답 묶음과 얼마나 맞는지 점수(1이 완벽).

## 1. 확정 구성 (그대로 옮긴다)

| 항목 | 값 | 근거 |
|---|---|---|
| 임베딩 모델 | `gemini-embedding-001` (Gemini) | DECISIONS 2026-07-22 P06/KAN-279 |
| 용도(task_type) | `SEMANTIC_SIMILARITY` | 5종 중 최고 |
| 차원 | `768` | 1536보다 높고 저렴 |
| 입력 텍스트 | 제목 + 짧은 요약(`summary_short`) | 상세요약은 Gemini엔 해로움 |
| 합치는 기준값 | 코사인 유사도 **0.86** | 0.01 스윕 최고점 |
| 비교 시간 범위 | **최근 24시간** | 늘리면 오히려 손해(KAN-289) |
| 벡터 정규화 | L2 정규화(길이 1) | 코사인=내적으로 계산 |
| 묶는 방식 | 발행 시각 순 하나씩(순차) · 대표값 **첫 기사(seed)** | KAN-287 |
| 애매한 구간 | 유사도 0.80~0.90은 **LLM 판정**(OpenAI gpt-4o-mini) | KAN-288 |

**성능(정답 라벨 90건 기준):** 배치 전체 묶기 ARI 0.9287. 운영형 순차 묶기는
seed 0.8636 → **애매한 구간 LLM 판정을 얹어 0.9149(잘못 합침 0)** 로, 배치에
근접한 순차 최고 성적.

## 2. 무엇을 어디로 옮기나 (모듈 경계)

### 2.1 그대로 옮기는 코드 (로직·계약 유지)

| 이 리포 모듈 | 하는 일 | 이식 메모 |
|---|---|---|
| `providers/base.py` | 공급자 인터페이스(`embed` → L2 정규화 (N, dim)) | 그대로. 계약이 경계 |
| `providers/gemini.py` | Gemini 임베딩 + 재시도(지수 백오프) | 그대로. 캐시 주입부만 저장소에 맞춤 |
| `pipeline/incremental.py` | 순차 묶기(`cluster_incrementally`) | **핵심 알고리즘. 그대로 옮김** |
| `pipeline/gray_zone.py` + `judge.py` | 애매한 구간만 LLM에 "같은 이슈?" 물음 | 그대로. 판정 캐시 유지 |
| `pipeline/articles.py` | 입력 텍스트 구성(`title_short`) | 그대로 |

### 2.2 갈아끼우는 부분 (운영에서 바뀜)

| 이 리포 | 운영(plick-ai/admin-server) | 이유 |
|---|---|---|
| `providers/cache.py` (`.npy` 파일 캐시) | 저장소 조회로 대체 가능 | 벡터를 저장소가 이미 들고 있음 |
| `pipeline/store.py` (로컬 파일 JSONL) | **Postgres(메타·관계) + 벡터DB(벡터)** | 규모·추천/검색 대비(DECISIONS KAN-290) |
| `pipeline/source.py` (Supabase 증분 로더) | plick-ai의 실제 입력 경로 | 서버 트리거로 바뀜 |
| `scripts/run_pipeline.py` (CLI 배치) | 서버 핸들러/워커 | HTTP·큐 트리거 |

> 저장소만 인터페이스(§3.1) 뒤에서 갈아끼우면 묶기 로직은 손대지 않는다.

### 2.3 안 옮기는 것 (실험 전용)

`eval/`(채점), `report/`·`wiki.py`(실험 노트), `results/`, 각종 `sweep_*`·
`compare_*`·`experiment_*` 스크립트 — 벤치마크용이라 운영에 불필요.

## 3. 인터페이스 계약 초안

### 3.1 저장소(Store) — 이식 시 벡터DB 어댑터로 교체할 경계

```
add(records)              # 기사 벡터 + 메타 저장 (이미 있는 id는 무시)
known_ids() -> set        # 이미 처리한 기사 id (건너뛰기용)
active_since(cursor)      # 최근 N시간 안 살아 있는 이슈의 대표 벡터 조회 (운영 추가)
set_issues(id -> issue)   # 묶기 결과(어느 이슈인지) 기록
```

저장 레코드(한 건)에 **반드시 함께** 담기는 메타:
`vector`, `model`, `task_type`, `dim`, `normalized`, `published_at`, `issue_id`.

- 이 리포: `all()`로 전체를 읽어 **매번 전부 다시 묶는다(방식 A)** — 90~150건이라
  충분·결정적.
- 운영: `active_since`로 **최근 N시간 후보만** 뽑아 새 기사만 이어붙인다(방식 B).
  후보가 작아 ANN(근사 최근접) 불필요 — pgvector/브루트포스로 충분.

### 3.2 공급자(Provider)

`embed(texts) -> (len(texts), dim)` L2 정규화 float32. 실패 시 재시도(백오프).
같은 텍스트는 두 번 부르지 않는다(캐시/저장소).

### 3.3 순차 묶기(cluster_incrementally)

입력: 정규화 벡터 (N, dim), 발행 시각 목록, `threshold=0.86`, `window=24h`,
`representative="seed"`. 출력: 입력 순서에 맞춘 이슈 라벨 (N,). 랜덤성 없음(결정적).

### 3.4 애매한 구간 LLM 판정(gray zone)

유사도가 [0.80, 0.90]에 걸린 결정만 LLM에 묻는다. **후보 묶음 전체**를 보여주고
"이슈=협상→메디컬→확정으로 이어지는 한 사건" 프롬프트로 물어야 사가를 안 쪼갠다
(첫 기사만 비교하면 ARI 붕괴 — KAN-288). 응답은 캐시.

## 4. 운영 흐름 (plick-ai 실시간)

```
새 기사 1건
  → (카테고리·주체·최근 24시간) 필터로 후보 이슈 조회   [저장소]
  → 후보 대표 벡터와 코사인 유사도 계산
  → ≥0.86 이면 그 이슈에 붙임 / <0.80 이면 새 이슈
  → 0.80~0.90 애매하면 LLM 판정                       [gray zone]
  → 결과(issue_id)를 저장                              [저장소]
```
기사당 **임베딩 1회 저장** — 전체 재임베딩 아님. 24시간은 저장 벡터의 **조회 조건**.

## 5. 미결정 항목 (이식 시 결정)

- **주체 연결(KAN-275, 진행 중):** 여러 날 이어지는 사가는 시간 축으로 못 풂 →
  날짜 건너 같은 인물/팀으로 이어 주기. 1단계 분류 LLM이 주체(타입+영어 이름)를
  요약과 함께 출력, admin-server의 인물 카탈로그에 대조. 이게 남은 잘못 나뉨의 해법.
- **추천·검색용 벡터DB 도입 시점:** dedup만이면 pgvector 한 곳으로 충분. 추천·숏폼·
  개인화(전체에서 비슷한 것 찾기 = ANN)가 붙을 때 전용 벡터DB로 분리(DECISIONS KAN-290).
- **저장소 구현체:** Postgres 확정. 벡터를 pgvector 한 컬럼으로 둘지, 전용 벡터DB로
  나눌지는 위 도입 시점과 함께 결정.
- **노이즈("검수 필요" placeholder) 처리:** 묶기가 아니라 상류 요약 품질 게이트에서.

## 6. 검증 근거 (수치)

- 임베딩 최종 선정 4축 비교: `wiki/최종선정_임베딩구성.md`,
  `wiki/트랙비교_Gemini_vs_OpenAI.md`
- 순차 묶기·대표값·애매구간·사가: `docs/pipeline.md` Phase 07 로그, DECISIONS
  2026-07-23 KAN-285~289
- 팀 공유 요약: `docs/CONFLUENCE_UPDATE.md`
- 이 리포 파이프라인: `pipeline/{source,store,batch,incremental,gray_zone}.py`,
  `scripts/run_pipeline.py` (90건 2회 연속 멱등 확인)
