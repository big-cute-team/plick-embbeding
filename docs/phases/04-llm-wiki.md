# Phase 04 — LLM Wiki (Obsidian) 구축

## 목표

리포 안에 Obsidian vault(`wiki/`)를 만들고, 실험을 돌릴 때마다 결과 노트가
자동 생성되어 쌓인다. 이후 모든 실험(Phase 05~)은 이 wiki에 기록되고,
모델·개념 노트로 지식이 누적되어 두 사람이 서로의 실험을 참고할 수 있다.

## 작업

- [ ] P04-T01 vault 구조 생성 — `wiki/00-INDEX.md`(MOC: 실험 목록·현재 최적
      구성), `wiki/experiments/`, `wiki/models/`, `wiki/concepts/`,
      `wiki/templates/`
- [ ] P04-T02 실험 노트 템플릿 — frontmatter(model, task_type, dim,
      threshold, window, dataset, ari, pairwise_f1, date, 담당자) + 본문
      섹션(조건·결과·해석·다음 시도). Confluence 실험 기록 가이드 템플릿과
      항목 호환
- [ ] P04-T03 자동 생성 연동 — 실험 실행 시 `results/<타임스탬프>/`와 함께
      `wiki/experiments/YYYY-MM-DD_HHMM_요약.md` 노트를 자동 생성하고
      INDEX에 한 줄 추가
- [ ] P04-T04 지식 노트 시드 — 모델 노트 2개(gemini-embedding-001,
      text-embedding-3), 개념 노트(task_type, ARI, 회색지대, 24h 윈도우,
      오병합·사가 분할)를 기존 Confluence 리서치 요지로 작성, `[[링크]]` 연결
- [ ] P04-T05 기존 실험 4건(Confluence 실험 기록 폴더) 백필 — 과거 결과도
      wiki에서 검색·비교 가능하게

## 변경 범위

`wiki/`, `src/plick_embedding/report/`, `scripts/`, `tests/`,
`docs/PROGRESS.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`(구조 반영)

## 완료 조건

- [ ] `wiki/`를 Obsidian에서 vault로 열면 INDEX → 실험/모델/개념 노트로
      링크 이동이 된다
- [ ] 실험 1회 실행 시 노트 1개가 자동 생성되고 frontmatter에 조건·점수가
      들어 있다 (테스트로 검증)
- [ ] 기존 실험 4건이 `wiki/experiments/`에 백필되어 있다
- [ ] 모델 노트 2개·개념 노트 5개 이상이 존재하고 서로 링크되어 있다

## 개발자 테스트

- [ ] Obsidian으로 `wiki/` 열어 그래프 뷰·링크 동작 확인
- [ ] `uv run python scripts/run_experiment.py ...` 실행 후 `wiki/experiments/`에 새 노트와 INDEX 갱신 확인
- [ ] 팀원(2인) 모두 vault를 열어 같은 내용이 보이는지 확인 (git pull 기준)
