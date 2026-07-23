"""전체 처리 흐름 — 가져오기 → 벡터 → 저장 → 묶기 → 어느 이슈인지 적기 (T03).

한 번 실행하면: 저장소에 없는(=아직 안 본) 기사만 골라 벡터로 만들어 저장하고,
저장된 벡터 전체를 발행 시각 순으로 다시 훑어 묶은 뒤(cluster_incrementally),
"이 기사는 어느 이슈"인지(issue_id)를 저장소에 적는다.

다시 실행하면 이미 저장된 기사는 다시 만들지 않는다(두 번 돌려도 결과가 같다).
전부 다시 묶는 건 발행 순서대로 한 건씩 처리라 결과가 똑같아 안전하다(방식 A).
"""

from dataclasses import dataclass
from datetime import timedelta

import numpy as np

from plick_embedding.pipeline.articles import Article, embed_texts
from plick_embedding.pipeline.incremental import cluster_incrementally
from plick_embedding.pipeline.store import StoredArticle, VectorStore
from plick_embedding.providers.base import EmbeddingProvider


@dataclass
class PipelineResult:
    new_count: int  # 이번에 새로 벡터로 만든 기사 수
    total: int  # 저장소 전체 기사 수
    issue_count: int  # 묶인 이슈 수


def run_pipeline(
    articles: list[Article],
    provider: EmbeddingProvider,
    store: VectorStore,
    threshold: float,
    window: timedelta,
    representative: str = "seed",
    input_mode: str = "title_short",
) -> PipelineResult:
    """기사 목록을 흐름에 태워 저장소를 갱신하고 요약을 반환한다.

    provider는 캐시를 품고 있어(공급자 규약), 같은 텍스트는 API를 다시 부르지 않는다.
    저장소에 이미 있는 기사 id는 아예 임베딩 대상에서 빠진다(이중 안전장치).
    """
    config = provider.config
    known = store.known_ids()

    new_articles = [a for a in articles if a.id not in known]
    if new_articles:
        vectors = provider.embed(embed_texts(new_articles, input_mode))
        store.add(
            [
                StoredArticle(
                    id=a.id,
                    published_at=a.published_at,
                    vector=vectors[i],
                    model=config.model,
                    task_type=config.task_type,
                    dim=config.dim,
                    normalized=True,
                )
                for i, a in enumerate(new_articles)
            ]
        )

    stored = store.all()
    embeddings = np.vstack([s.vector for s in stored])
    labels = cluster_incrementally(
        embeddings,
        [s.published_at for s in stored],
        threshold=threshold,
        window=window,
        representative=representative,
    )
    store.set_issues({s.id: f"issue_{label}" for s, label in zip(stored, labels, strict=True)})

    return PipelineResult(
        new_count=len(new_articles),
        total=len(stored),
        issue_count=len(set(labels)),
    )
