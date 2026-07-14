# plick-embedding

PLick의 "같은 이슈 묶기(원문 N : 요약 1)"를 위한 **임베딩 벤치마크·실험
리포**. Google Gemini와 OpenAI 임베딩을 정량 비교해 최적 구성(모델 ·
task_type · 차원 · 임계)을 선정하고, 그 구성으로 수집→임베딩→벡터
저장→증분 dedup 파이프라인을 검증한다. 검증된 결과는 plick-ai(FastAPI)로
이식한다.

## 실행 / 테스트

```bash
uv sync                                          # 의존성 설치
uv run pytest                                    # 테스트
uv run ruff check .                              # 린트
uv run python scripts/run_experiment.py --help   # 실험 실행 CLI
```

API 키는 `.env`에 설정한다 (`.env.example` 참조).

## 문서

- 진행 상황: [docs/PROGRESS.md](docs/PROGRESS.md)
- 스펙·제외 범위: [docs/SPEC.md](docs/SPEC.md)
- 구조·명령: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- 배경·Confluence 정본 링크: [docs/BRIEF.md](docs/BRIEF.md)
