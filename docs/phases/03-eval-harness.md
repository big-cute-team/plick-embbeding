# Phase 03 — 정답 라벨 + 정량 평가 러너

## 목표

"눈 검증"을 정량화한다. 실데이터 셋에 정답 이슈 라벨을 붙이고, 어떤 실험
결과든 ARI·pairwise precision/recall 점수가 자동으로 나온다. 이 점수가
Phase 04 벤치마크의 채점 기준이 된다.

## 작업

- [ ] P03-T01 라벨 포맷 정의 — `data/labels/`에 (기사 id → 정답 이슈 id)
      매핑 파일 형식과 로더 구현
- [ ] P03-T02 published 56건 셋에 정답 라벨 부여 — 기존 실험 기록의
      군집·오병합 메모를 초안으로 삼고, 최종 확정은 개발자 검수
- [ ] P03-T03 지표 러너 구현 — ARI, pairwise precision/recall/F1,
      오병합·과분할 사례 목록 출력
- [ ] P03-T04 리포트에 지표 섹션 통합 — 실험 실행 시 라벨이 있으면 점수가
      report에 자동 포함
- [ ] P03-T05 기존 잠정 구성(SEMANTIC@0.85)의 기준 점수(baseline) 측정·기록

## 변경 범위

`src/plick_embedding/eval/`, `src/plick_embedding/report/`, `scripts/`,
`data/labels/`, `tests/`, `docs/PROGRESS.md`, `docs/DECISIONS.md`

## 완료 조건

- [ ] 라벨 파일이 로드되고, 라벨 없는 기사가 있으면 명시적으로 경고한다
- [ ] 같은 군집 결과에 대해 지표 러너가 결정론적으로 같은 점수를 낸다
      (테스트로 고정)
- [ ] SEMANTIC@0.85 baseline의 ARI·pairwise 점수가 report와
      `docs/DECISIONS.md`에 기록돼 있다
- [ ] 알려진 오병합 2건(제임스+라이스, 기마랑이스+토날리)이 오병합 사례
      목록에 잡힌다

## 개발자 테스트

- [ ] `uv run python scripts/run_experiment.py ... --labels data/labels/published56.json` 실행 후 report에서 ARI 점수 확인
- [ ] 오병합 사례 목록에 기존에 눈으로 발견한 2건이 있는지 확인
- [ ] 라벨 초안 검수: `data/labels/published56.json`을 열어 이슈 배정이 맞는지 확인
