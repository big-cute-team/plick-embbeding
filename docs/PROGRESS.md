# PROGRESS

> 프로젝트 상태의 단일 소스. 모든 세션은 이 파일을 읽고 시작하고,
> 이 파일을 갱신하고 끝난다. 형식(섹션 이름, Status 값)을 바꾸지 말 것.

## Current Phase

05 — 모델별 task_type 실험 (2인 병렬: Gemini / OpenAI) (`docs/phases/05-parallel-experiments.md`)

## Current Task

P05-T07 (트랙 B 실험 실행 — 매트릭스 승인 대기)

## Status

IN PROGRESS

## Completed

- [x] Phase 01 — 프로젝트 뼈대
- [x] Phase 02 — PoC 이관 + 기준선 확립
- [x] Phase 03 — 정답 라벨 + 정량 평가 러너 (검토 통과)
- [x] Phase 04 — LLM Wiki (Obsidian) 구축 (검토 통과)
- [ ] Phase 05 — 모델별 task_type 실험 (2인 병렬: Gemini / OpenAI)
- [ ] Phase 06 — 결과 종합 · 최적 구성 선정
- [ ] Phase 07 — 증분 중복 묶기 + 예외 케이스
- [ ] Phase 08 — 수집→임베딩→벡터 저장 파이프라인

## Working Notes

- 2026-07-15 Phase 05 트랙 B — T01·T05·T06 완료(비용 없는 부분). T01
  wiki/plans/공통 실험 기준.md, T05 wiki/plans/트랙B_OpenAI_매트릭스.md
  (모델 small/large × 차원 768/1536 × 임계 0.30~0.65 훑기, 임베딩 4세트),
  T06 providers/openai.py(text-embedding-3, dimensions 옵션·캐시·백오프,
  task_type 없음→"none") + 러너 연동(--model openai-small/large) + 테스트
  (총 26개 통과). INDEX에 plans/ 섹션 추가. 남은 것: T07 유료 실험(4세트,
  예상 ~$0.002)은 매트릭스 승인 후 실행 → T08 요약. 트랙 A(Gemini)는 팀원 몫.
  ※ Phase 05는 두 트랙·유료 실험이 남아 IN PROGRESS 유지(부분 완료).
- 2026-07-15 Phase 04 완료 (검토 대기). 만든 것: wiki/00-INDEX.md(목차+현재
  최적 구성+위키 작성 규칙), templates/experiment-note.md(노트 양식),
  report/wiki.py(실험 실행 시 wiki/experiments/에 노트 자동 생성+목차 행
  추가/교체, run_experiment.py 연동), 모델 노트 2(gemini·text-embedding-3)·
  개념 노트 5(task_type·ARI·회색지대·최근 24시간만 비교·잘못 합침과 사가 분할),
  과거 실험 4건 백필(Confluence 14843913에서: published56 SEMANTIC 26/15·
  CLUSTERING 27/14, published34 각 14/8), tests/test_wiki.py 5개(깨진 링크·
  목차 누락·자동 생성, 총 25개 API 없이 통과)·ruff 통과. 카파시 패턴 대조로
  보강한 3가지(작성 규칙·노트 자급자족·자동 점검) 모두 반영. 기준선 노트
  자동 생성 확인: 2026-07-15_articles90_SEMANTIC_0.85_24h(ARI 0.9071·F1 0.9091).
  참고: 개발자는 Obsidian으로 wiki/ 열어 그래프·링크를 눈으로 확인 필요.
- 2026-07-15 Phase 04 착수 — 계획: wiki/, 노트 양식, report/wiki.py 자동 생성,
  모델·개념 노트, 과거 실험 4건 백필, 링크·목차 점검 테스트.
- 2026-07-15 열린 항목 2개를 Phase 05로 이월(DECISIONS 기록) — (1) 이적 사가를
  소식 단위로 쪼갤지(개발자 잠정: 분리 쪽, 미확정), (2) 임베딩 입력 텍스트 구성을
  비교 축으로. article_summaries에 summary_detail(~148자, 현재 쓰는 summary_short의
  3.5배)·category·rumor_stage 존재 확인 → "제목만/제목+짧은요약/제목+상세요약"
  실험 가능. 입력 텍스트 확정 시 라벨도 함께 재검토. 현재 기준선(사가=1개,
  제목+짧은요약)은 그대로 유지.
- 2026-07-15 용어 쉬운 말로 전면 정리(프로젝트 전반) — 오병합→"잘못 합침",
  과분할→"잘못 나뉨", (24h)윈도우/롤링 윈도우→"최근 24시간만 비교"/"비교 시간
  범위". 문서·리포트 출력·주석·테스트의 사람이 읽는 텍스트만 변경, 코드 식별자
  (window_hours, split_clusters_by_window, --window 옵션)는 유지. 리포트 지표도
  풀어씀(ARI="정답과 얼마나 일치하나", 쌍 정밀도/재현율="맞게 묶은 비율/찾아낸
  비율"). 규칙은 docs/CONVENTIONS.md "용어 — 쉬운 말로 쓰기" 절에 표로 고정.
  테스트 20개·ruff 통과, 기준선 점수 불변(리포트만 새 문구로 재생성).
- 2026-07-15 P03 검수 수정 반영 — 개발자가 라벨 원칙을 "같은 이슈 = 똑같은
  사건, 본문으로 판정"으로 확정. 정답지 오류 1건 정정: 7358 "맨유, 두 미드필더
  £85m 발표 임박"은 틸레망스 명시가 없어(오히려 £35m 단독 이적과 불일치)
  tielemans_manutd→manutd_two_midfielders_85m 단독 이슈로 변경. 재채점(캐시,
  API 없음): ARI 0.8569→0.9071, F1 0.8602→0.9091, 재현율 0.7921→0.8791
  (FN 21→11, 틸레망스 허위 잘못 나뉨 제거), 잘못 합침 2건 유지·잘못 나뉨 7→6.
  기준선 폴더 results/20260715_102026/. 검토에서 확인된 것: 데리(첼시 계약 vs
  스포르팅 임대) 이미 분리 정답, 홀란 3건(소감/교체/응원) 분리 정답 —
  잘못 합침으로 정상 포착. 테스트 20개·ruff 통과.
- 2026-07-14 Phase 03 완료 (검토 대기). 만든 것: eval/labels.py(정답 로더
  {기사id:이슈id}+미라벨 경고), data/labels/articles90.json(90건→이슈 55개
  정답 초안, 다건 15·단건 40), eval/scoring.py(ARI·쌍 정밀도/재현율/F1·
  잘못 합침/잘못 나뉨, 결정론), report에 정량 평가 섹션+scores.json 연결,
  run_experiment.py --labels. tests/test_eval.py 7개 추가(총 20개, API 없이
  통과)·ruff 통과. 기준선 점수(SEMANTIC@0.85, 90건, 768d, 24h): ARI 0.8569,
  쌍 정밀도 0.9412·재현율 0.7921·F1 0.8602(TP80/FP5/FN21), 잘못 합침 2건(홀란
  경험·교체·응원 3중, 이라올라 계약+계획)·잘못 나뉨 7건, results/20260714_210532/.
  ⚠️ 정답 초안 검수 필요(개발자): (1) 라벨 판단이 애매한 건 —
  7358(틸레망스에 포함시켰으나 임베딩은 분리), 7092(manutd_extra_midfielder
  단독 처리), 지미제이 데리 첼시 계약 vs 스포르팅 임대 분리, 홀란 미세뉴스
  분할 기준. (2) 라벨은 최근 24시간만 비교 무관 "실제 사건" 기준이라, 여러 날 사가는
  잘못 나뉨으로 잡히게 설계함(DECISIONS 참조) — 이 관점이 맞는지 확인.
- 2026-07-14 Phase 03 착수 — 계획: eval/labels.py, articles90.json,
  eval/scoring.py, report 연결, T05 기준 점수.
- 2026-07-14 P02-T05 완료 → Phase 02 전체 완료 (검토 대기). `.env`에
  GEMINI_API_KEY 주입 후 기준선 실험 실행: gemini-embedding-001 ·
  SEMANTIC_SIMILARITY · 768d · 임계 0.85 · 24h → 결과 90건 → 60이슈 /
  중복묶음 12개 (분포 1×48,2×6,3×3,5×1,6×1,10×1). 결과·눈 검증 코멘트는
  `results/20260714_204902/`. 캐시 재실행 0.8초·API 없이 동일 수치 재현,
  테스트 13개·ruff 통과. 눈 검증 요지: 단일 이적 사건(틸레망스 10건 등)은
  임계 0.85로 정확·표기 변형까지 흡수. 놓친 것 다수는 모델이 아니라
  최근 24시간만 비교가 여러 날 사가(에데르송·잉글랜드 훈련)를 자른 것 + 선수
  미세뉴스(홀란)의 "같은 이슈" 경계 모호 → Phase 03 라벨·05 벤치마크에서
  정밀 판정. 참고: 개발자가 키를 처음 `.env.local`에 넣었으나 러너는 `.env`를
  읽음 → 개발자가 `.env`로 전체 이관해 해결.
- 2026-07-14 P02-T01 완료 — `.env.local`의 Supabase 접근 정보로
  article_summaries에서 PUBLISHED 기사 90건(published_at 2026-07-09~13 UTC)을
  추출해 `data/articles.json` 고정 (`scripts/fetch_articles.py`, 기존 파일
  덮어쓰기 거부). 파이프라인 로더로 로드 검증, 테스트 13개·ruff 통과.
  남은 것: T05 기준선 실험 — GEMINI_API_KEY가 `.env`에 없어 블록 (Blockers 참조).
- 2026-07-14 기존 데이터셋(기사 56건·tmp_embeddings) 소실 확인 → Phase 02를
  "재현"에서 "새 데이터셋 기준선 확립"으로 재구성 (phase 파일·DECISIONS 갱신).
  T01=새 스냅샷 고정, T05=잠정 구성 기준선 실험+눈 검증. T02~T04 코드는 그대로 유효.
- 2026-07-14 Phase 02 T02~T04 구현 완료 (트랙 A) — providers(base/cache/
  gemini: task_type·차원 옵션, L2 정규화, .npy 파일 캐시, 지수 백오프),
  pipeline(articles 로더·병합형 군집화·시간 범위로 나누기), report(results/
  <타임스탬프>/ config+result+report.md). 테스트 13개(API 없이 통과).
  비교 시간 범위 적용 방식은 DECISIONS.md 참조 (T05에서 검증 필요).
- 남은 것: T01(데이터)·T05(재현) — 기사 56건+tmp_embeddings 접근 정보 필요.
  로컬 plick-ai/prototype 리포에는 poc-embedding 코드·데이터 없음 확인.
  입력 형식은 data/articles.json: [{id, title, summary_short, published_at}].
- 2026-07-14 Phase 01 완료 (트랙 A) — pyproject.toml(uv, Python 3.12),
  src/plick_embedding/{providers,pipeline,eval,report}, settings 모듈(.env 로드,
  키 값 비노출 summary), scripts/run_experiment.py 뼈대(--help/--show-config),
  테스트 3개·ruff 설정. `.gitignore`에 `!.env.example` 예외 추가
  (`.env.*` 규칙이 견본 파일까지 무시하던 문제). 완료 조건 4개 전부 통과.
  다음 세션 참고: Phase 02는 기존 실험 데이터(published 56건·tmp_embeddings)
  접근 정보가 필요 — 개발자 제공 대기.
- 2026-07-14 init-project로 초기화됨 (Confluence 설계·실험 문서 분석 기반).
  Phase 01부터 시작.
- 2026-07-14 문서 전체 용어 정리 — dedup→중복 묶기, Agglomerative→병합형
  군집화, vault→보관함 등 (가독성).
- 2026-07-14 Phase 01~04 병렬 트랙 확정 — 트랙 A(개발: 01→02→03 러너) /
  트랙 B(지식·라벨: 04 보관함·노트 → 03 라벨). 티켓 6장 분리안은
  `docs/phases/README.md`의 "병렬 진행 가이드" 참조.
- 2026-07-14 Confluence 게시 완료 — 마스터 문서(9175112 v24): §5.6 같은
  이슈 판정 3겹 규칙·§6.4 임베딩 역할 경계 신설, 기능2에 실험 리포 현황
  반영. 중복 처리 파이프라인(15171586 v4): 결정 트리 개정(낮은 티어 헤지
  편입)·재임베딩 규칙 확정. 초안 원본은 `docs/CONFLUENCE_UPDATE.md`.
- 2026-07-14 phase 01~08 작업(태스크) 설명을 쉬운 문장으로 전면 재작성
  (가독성 — 작업 ID·체크박스·완료 조건은 그대로).
- Phase 02 착수 전 필요: 기존 실험 데이터(published 56건·tmp_embeddings)
  접근 정보 — 개발자 제공 대기.

## Blockers

none

## Developer Test

none
