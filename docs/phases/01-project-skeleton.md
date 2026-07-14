# Phase 01 — 프로젝트 뼈대

## 목표

uv 기반 Python 프로젝트가 설치·테스트·린트·CLI 실행까지 동작한다.
이후 phase는 이 뼈대 위에 코드만 얹는다.

## 작업

- [ ] P01-T01 uv 프로젝트 초기화 — `pyproject.toml`(Python 3.12, numpy,
      scikit-learn, google-genai, openai, python-dotenv, pytest, ruff),
      `src/plick_embedding/` 패키지 레이아웃
- [ ] P01-T02 디렉토리 뼈대 생성 — `src/plick_embedding/{providers,pipeline,eval,report}/`,
      `scripts/`, `data/`, `tests/` (각 패키지에 `__init__.py`)
- [ ] P01-T03 설정 로딩 — `.env`에서 API 키를 읽는 settings 모듈 +
      `.env.example` 작성 (`GEMINI_API_KEY`, `OPENAI_API_KEY`)
- [ ] P01-T04 CLI 진입점 스텁 — `scripts/run_experiment.py`가 `--help`와
      설정 요약 출력까지 동작
- [ ] P01-T05 스모크 테스트 1개 + ruff 설정, `.gitignore`에 results/·캐시 확인

## 변경 범위

`pyproject.toml`, `uv.lock`, `.env.example`, `src/`, `scripts/`, `tests/`,
`.gitignore`, `docs/PROGRESS.md`

## 완료 조건

- [ ] `uv sync`가 에러 없이 끝난다
- [ ] `uv run pytest`가 1개 이상 테스트로 통과한다
- [ ] `uv run ruff check .`가 통과한다
- [ ] `uv run python scripts/run_experiment.py --help`가 사용법을 출력한다

## 개발자 테스트

- [ ] `uv sync && uv run pytest && uv run ruff check .` 한 줄로 전부 통과 확인
- [ ] `uv run python scripts/run_experiment.py --help` 출력 확인
