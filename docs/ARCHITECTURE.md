# ARCHITECTURE

## 기술 스택

- **Python 3.12** + **uv** (의존성·가상환경 관리, `pyproject.toml`)
- **numpy / scikit-learn** — 코사인 유사도, 병합형 군집화(Agglomerative), ARI 등 지표
- **google-genai / openai** — 임베딩 API 클라이언트 (공급자 추상화 뒤에 둠)
- **pytest** (테스트) / **ruff** (린트+포맷)
- 서버 프레임워크 없음 — CLI 스크립트로 실행하는 실험·배치 리포
- **Obsidian** — `wiki/`를 보관함(vault)으로 열어 실험 기록·지식 노트 관리 (git으로 공유)
- 벡터 저장: 초기엔 로컬 파일(npz/parquet) 캐시. 벡터DB vs MySQL은
  Phase 08에서 Research 후 결정

## 디렉토리 구조

```
plick-embbeding/
├── src/plick_embedding/
│   ├── providers/     # Gemini·OpenAI 임베딩 클라이언트 (공통 인터페이스 + 캐시)
│   ├── pipeline/      # 후보 좁히기(최근 24시간만 비교) · 군집화 · 증분 중복 묶기
│   ├── eval/          # 정답 라벨 로드 · ARI · 쌍 단위 정밀도·재현율(pairwise)
│   └── report/        # 실험 리포트 생성 (Confluence 실험 기록 템플릿 형식)
├── scripts/           # 실험 실행 CLI (run_experiment.py 등)
├── data/              # 입력 스냅샷 · 정답 라벨 (작은 파일만 커밋)
├── results/           # 실행별 산출물 results/<타임스탬프>/ (gitignore)
├── wiki/              # Obsidian 보관함(vault) — LLM Wiki (커밋함)
│   ├── 00-INDEX.md    #   목차 노트: 실험 목록 · 현재 최적 구성
│   ├── experiments/   #   실험 1회 = 노트 1개 (report 모듈이 자동 생성)
│   ├── models/        #   모델별 지식·누적 결과 (gemini, text-embedding-3)
│   ├── concepts/      #   task_type · ARI · 회색지대 등 개념 노트
│   └── templates/     #   실험 노트 템플릿
├── tests/
└── docs/
```

## 주요 컴포넌트와 데이터 흐름

1. **데이터 로드** — 기사 스냅샷(title + summary_short)을 data/ 또는 원본
   저장소(읽기 전용)에서 가져온다.
2. **임베딩** — providers/의 공통 인터페이스로 모델·task_type·차원을 바꿔
   호출. 같은 (텍스트 × 모델 × task_type × 차원) 조합은 캐시에서 재사용
   (API 재호출 금지).
3. **후보 좁히기 + 군집화** — 최근 24시간만 비교로 비교 대상을 좁히고,
   전역 병합형 군집화(cosine, average) 또는 증분 중복 묶기으로 이슈 제안.
4. **평가** — 정답 라벨과 비교해 ARI(군집 일치 점수)·쌍 단위 지표 산출.
5. **리포트 → Wiki** — results/<타임스탬프>/에 config·result·report를
   저장하고, 같은 실행에서 `wiki/experiments/`에 실험 노트를 자동 생성한다
   (머리말에 조건·점수). 팀 차원 공유가 필요한 결과는 Confluence
   실험 기록 폴더에 요약 페이지로 올린다.

## 실행 / 테스트 명령

```bash
uv sync                                          # 의존성 설치
uv run pytest                                    # 테스트
uv run ruff check . && uv run ruff format --check .  # 린트/포맷 확인
uv run python scripts/run_experiment.py --help   # 실험 실행 CLI
```
