# Phase 04 — LLM Wiki (Obsidian) 구축

## 목표

리포 안에 Obsidian 보관함(`wiki/`)을 만들고, 실험을 돌릴 때마다 결과 노트가
자동 생성되어 쌓인다. 이후 모든 실험(Phase 05~)은 이 wiki에 기록되고,
모델·개념 노트로 지식이 누적되어 두 사람이 서로의 실험을 참고할 수 있다.

## 작업

- [x] P04-T01 위키 폴더 만들기 — `wiki/` 아래에 목차 노트
      `00-INDEX.md`(실험 목록·현재 최적 구성)와 하위 폴더 4개를 만든다:
      `experiments/`(실험 기록), `models/`(모델 지식), `concepts/`(개념
      정리), `templates/`(노트 양식). 목차 노트에 **위키 작성 규칙** 절을
      함께 둔다: 노트 이름 짓는 법, 머리말에 넣을 항목, 언제 목차를
      갱신하는지 — 두 사람과 에이전트가 같은 형식으로 쓰게 하는 기준
- [x] P04-T02 실험 노트 양식 만들기 — 노트 맨 위 머리말(frontmatter)에
      실험 조건(model, task_type, dim, threshold, window, dataset)과
      점수(ari, pairwise_f1), 날짜·담당자를 적고, 본문은 조건·결과·해석·
      다음 시도 절로 구성. Confluence 실험 기록 가이드와 항목을 맞춘다.
      **노트만 읽어도 실험을 이해할 수 있어야 한다** — `results/`는 git에
      안 올라가 팀원에게 안 보이므로, 점수·묶음 수·대표 사례(잘 묶인 것/
      잘못 합침/잘못 나뉨 각 1개 이상)를 노트 본문에 직접 담는다
- [x] P04-T03 노트 자동 생성 연동 — 실험을 돌리면 결과 폴더와 함께
      `wiki/experiments/YYYY-MM-DD_HHMM_요약.md` 노트가 자동으로 만들어지고
      목차(INDEX)에도 한 줄 추가되게 한다
- [x] P04-T04 기초 지식 노트 쓰기 — 모델 노트 2개(gemini-embedding-001,
      text-embedding-3)와 개념 노트 5개(task_type, ARI, 회색지대, 24h
      비교 시간 범위, 잘못 합침·사가 분할)를 기존 Confluence 리서치 요지로 작성하고
      서로 `[[링크]]`로 연결한다
- [x] P04-T05 과거 실험 옮겨 적기 — Confluence 실험 기록 폴더의 기존 실험
      4건을 위키 노트로 백필해서, 과거 결과도 위키에서 검색·비교할 수
      있게 한다

## 변경 범위

`wiki/`, `src/plick_embedding/report/`, `scripts/`, `tests/`,
`docs/PROGRESS.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`(구조 반영)

## 완료 조건

- [x] `wiki/`를 Obsidian에서 보관함(vault)으로 열면 INDEX → 실험/모델/개념 노트로
      링크 이동이 된다
- [x] 실험 1회 실행 시 노트 1개가 자동 생성되고 머리말에 조건·점수가
      들어 있다 (테스트로 검증)
- [x] 기존 실험 4건이 `wiki/experiments/`에 백필되어 있다
- [x] 모델 노트 2개·개념 노트 5개 이상이 존재하고 서로 링크되어 있다
- [x] 위키 자동 점검 테스트가 있다 — 깨진 `[[링크]]`(대상 노트 없음)와
      목차 누락(experiments/ 노트가 INDEX에 없음)을 잡아내며, 전체
      테스트와 함께 API 없이 통과한다

## 개발자 테스트

- [ ] Obsidian으로 `wiki/` 열어 그래프 뷰·링크 동작 확인
- [ ] `uv run python scripts/run_experiment.py ...` 실행 후 `wiki/experiments/`에 새 노트와 INDEX 갱신 확인
- [ ] 팀원(2인) 모두 보관함을 열어 같은 내용이 보이는지 확인 (git pull 기준)
