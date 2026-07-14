# Phase 01 — 프로젝트 뼈대

## 목표

uv 기반 Python 프로젝트가 설치·테스트·린트·CLI 실행까지 동작한다.
이후 phase는 이 뼈대 위에 코드만 얹는다.

## 작업

- [x] P01-T01 프로젝트 기본 설정 만들기 — 쓸 라이브러리 목록을 담은
      `pyproject.toml`(Python 3.12 / numpy, scikit-learn, google-genai,
      openai, python-dotenv, pytest, ruff)과 코드가 들어갈 패키지 폴더
      `src/plick_embedding/`를 만든다
- [x] P01-T02 폴더 구조 잡기 — 역할별 하위 폴더를 만든다:
      `src/plick_embedding/{providers,pipeline,eval,report}/`(임베딩 제공자 /
      묶기 로직 / 채점 / 리포트), `scripts/`, `data/`, `tests/`
      (파이썬 패키지마다 `__init__.py` 포함)
- [x] P01-T03 API 키 설정 — `.env` 파일에서 Gemini·OpenAI API 키를
      읽어오는 settings 모듈을 만들고, 팀원이 참고할 견본 파일
      `.env.example`(`GEMINI_API_KEY`, `OPENAI_API_KEY`)도 만든다
- [x] P01-T04 실행 명령 뼈대 — `scripts/run_experiment.py`를 만들어
      `--help` 사용법과 현재 설정 요약이 출력되게 한다
      (실제 실험 로직은 다음 phase에서)
- [x] P01-T05 검증 도구 세팅 — 프로젝트가 제대로 도는지 확인하는 테스트
      1개, 코드 스타일 검사(ruff) 설정, 실험 결과물(`results/`)과 캐시가
      git에 올라가지 않도록 `.gitignore` 정리

## 변경 범위

`pyproject.toml`, `uv.lock`, `.env.example`, `src/`, `scripts/`, `tests/`,
`.gitignore`, `docs/PROGRESS.md`

## 완료 조건

- [x] `uv sync`가 에러 없이 끝난다
- [x] `uv run pytest`가 1개 이상 테스트로 통과한다
- [x] `uv run ruff check .`가 통과한다
- [x] `uv run python scripts/run_experiment.py --help`가 사용법을 출력한다

## 개발자 테스트

- [ ] `uv sync && uv run pytest && uv run ruff check .` 한 줄로 전부 통과 확인
- [ ] `uv run python scripts/run_experiment.py --help` 출력 확인
