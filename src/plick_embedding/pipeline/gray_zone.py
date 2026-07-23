"""애매한 구간 LLM 판정을 얹은 하나씩 묶기.

기본 순차 묶기(`cluster_incrementally`)는 유사도 기준값 하나로 붙일지 정한다.
여기서는 최고 유사도가 **애매한 구간**[gray_low, gray_high]에 걸릴 때만 LLM에게
"이 두 기사가 같은 사건인가?"를 물어 그 답으로 붙일지 정한다:

- 최고 유사도 >= gray_high  → 확실히 비슷 → 그냥 붙임 (LLM 안 부름)
- 최고 유사도 <  gray_low   → 확실히 다름 → 새 묶음 (LLM 안 부름)
- 그 사이(애매)            → LLM에게 물어 예=붙임 / 아니오=새 묶음

벡터 비교의 대표값은 첫 기사(seed) 고정(KAN-287에서 선정)이지만, **LLM에는 후보 묶음의
기사 전체(지금까지의 스토리)를 보여준다** — 첫 기사 하나만 보면 이적 사가의 뒷단계
(메디컬·확정)를 "다른 사건"으로 오판해 쪼개기 때문. 판정기(judge)는
(새 기사 텍스트, 묶음 전체 텍스트) → bool 콜러블이라, 테스트에서는 스텁을 넣는다.
"""

from collections.abc import Callable
from datetime import datetime, timedelta

import numpy as np

Judge = Callable[[str, str], bool]


def cluster_with_gray_zone_judge(
    embeddings: np.ndarray,
    published_at: list[datetime],
    texts: list[str],
    threshold: float,
    window: timedelta,
    gray_low: float,
    gray_high: float,
    judge: Judge,
) -> tuple[np.ndarray, int]:
    """애매한 구간만 LLM에 물어 하나씩 묶는다. (라벨 (N,), LLM 판정 횟수)를 반환.

    threshold는 애매 구간 밖 참고용이 아니라, gray_high 이상만 자동 붙임·gray_low
    미만만 자동 새 묶음이라 사실상 구간 경계(gray_low·gray_high)가 판정을 가른다.
    라벨은 입력 순서에 맞춰 반환한다.
    """
    if not (len(embeddings) == len(published_at) == len(texts)):
        raise ValueError("embeddings·published_at·texts 길이가 다릅니다.")
    n = len(embeddings)
    if n == 0:
        return np.array([], dtype=int), 0

    order = sorted(range(n), key=lambda i: published_at[i])
    labels = np.full(n, -1, dtype=int)
    # 각 묶음: 첫 기사 벡터(rep), 소속 기사 텍스트 전체, 마지막 갱신 시각
    reps: list[np.ndarray] = []
    member_texts: list[list[str]] = []
    updated: list[datetime] = []
    n_judge_calls = 0

    for i in order:
        vec = embeddings[i]
        when = published_at[i]

        best = -1
        best_sim = -1.0
        for c in range(len(reps)):
            if when - updated[c] > window:
                continue
            sim = float(np.dot(vec, reps[c]))
            if sim > best_sim:
                best, best_sim = c, sim

        join = False
        if best >= 0:
            if best_sim >= gray_high:
                join = True
            elif best_sim < gray_low:
                join = False
            else:  # 애매한 구간 → 묶음 전체를 보여주고 LLM에 물어본다
                n_judge_calls += 1
                cluster_text = "\n---\n".join(member_texts[best])
                join = judge(texts[i], cluster_text)

        if join:
            labels[i] = best  # 라벨 = 묶음 인덱스
            member_texts[best].append(texts[i])
            updated[best] = when
        else:
            labels[i] = len(reps)
            reps.append(vec)
            member_texts.append([texts[i]])
            updated.append(when)

    return labels, n_judge_calls
