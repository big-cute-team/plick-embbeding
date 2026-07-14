# Phase 08 — 수집→임베딩→벡터 저장 파이프라인

## 목표

선정된 구성으로 실제 기사 데이터를 로드해 임베딩하고, 벡터를 저장하고,
증분 dedup까지 이어지는 배치 파이프라인이 반복 실행 가능하다. plick-ai
이식 기준(무엇을 어디로 옮기는지)이 문서화된다.

## 작업

- [ ] P08-T01 벡터 저장 방식 Research — 로컬/MySQL(JSON·BLOB + model·
      task_type·dim·normalized 메타) vs 벡터DB(Chroma 등), 현재 규모
      (하루치 후보 brute-force) 기준으로 결정해 DECISIONS 기록
- [ ] P08-T02 데이터 로더 — 원본 저장소(읽기 전용)에서 신규 기사를
      가져오는 증분 로더 (접속 정보는 개발자 제공)
- [ ] P08-T03 배치 파이프라인 — 로드 → 임베딩(캐시) → 벡터 저장 →
      온라인 dedup → 이슈 매핑 산출물 저장, 재실행 시 이어서 처리(멱등)
- [ ] P08-T04 실패 처리 — API 오류 재시도, 중단 후 재실행하면 이미 처리한
      기사를 건너뛰는지 검증
- [ ] P08-T05 plick-ai 이식 가이드 작성 — 선정 구성·모듈 경계·계약 초안을
      `docs/`에 정리 (구현 이식 자체는 plick-ai 리포에서)

## 변경 범위

`src/plick_embedding/`, `scripts/`, `tests/`, `docs/`,
`docs/PROGRESS.md`, `docs/DECISIONS.md`

## 완료 조건

- [ ] 벡터 저장 방식 결정과 근거가 `docs/DECISIONS.md`에 있다
- [ ] 파이프라인을 두 번 연속 실행하면 두 번째는 신규 기사만 처리한다
- [ ] 저장된 벡터에 model·task_type·dim·normalized 메타가 함께 있다
- [ ] 이식 가이드 문서가 선정 구성·경계·미결정 항목을 담고 있다

## 개발자 테스트

- [ ] `uv run python scripts/run_pipeline.py` 2회 연속 실행 — 2회차 로그에서 "신규 0건 또는 신규만 처리" 확인
- [ ] 저장소에서 벡터 1건을 꺼내 메타 필드 확인
- [ ] 이식 가이드를 읽고 plick-ai 반영 계획 수립 가능한지 판단
