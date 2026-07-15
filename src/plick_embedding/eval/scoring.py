"""채점기 — 예측 군집을 정답 라벨과 비교해 점수를 낸다.

지표:
- ARI (adjusted Rand index): 군집 배정이 정답과 얼마나 일치하는지 (-0.5~1.0).
- 쌍 단위(pairwise) 정밀도·재현율·F1: "같은 이슈면 같은 묶음" 관점에서
  기사 쌍을 맞췄는지. positive = 같은 정답 이슈인 쌍.
- 잘못 합침(overmerge): 예측 묶음 하나가 정답상 서로 다른 이슈를 섞은 경우.
- 잘못 나뉨(oversplit): 정답 이슈 하나가 예측에서 여러 묶음으로 쪼개진 경우.

정답이 없는 기사는 채점에서 제외한다 (경고는 호출부에서). 모든 계산은
결정론적 — 같은 입력이면 항상 같은 점수·같은 사례 목록(정렬 고정)을 낸다.
"""

from dataclasses import dataclass

import numpy as np
from sklearn.metrics import adjusted_rand_score

from plick_embedding.eval.labels import LabelSet
from plick_embedding.pipeline.articles import Article


@dataclass(frozen=True)
class PairwiseScore:
    precision: float
    recall: float
    f1: float
    tp: int
    fp: int
    fn: int


@dataclass(frozen=True)
class MergeCase:
    """잘못 합침 — 예측 묶음 하나에 정답 이슈가 둘 이상 섞임."""

    pred_cluster: int
    members_by_issue: dict[str, list[str]]  # 이슈 id → ["기사id 제목", ...]


@dataclass(frozen=True)
class SplitCase:
    """잘못 나뉨 — 정답 이슈 하나가 예측 묶음 여러 개로 흩어짐."""

    issue: str
    members_by_cluster: dict[int, list[str]]  # 예측 묶음 id → ["기사id 제목", ...]


@dataclass(frozen=True)
class ScoreResult:
    n_labeled: int
    n_unlabeled: int
    n_truth_issues: int
    n_pred_clusters: int
    ari: float
    pairwise: PairwiseScore
    overmerges: list[MergeCase]
    oversplits: list[SplitCase]


def _label(article: Article) -> str:
    return f"{article.id} {article.title}"


def _pairs(n: int) -> int:
    return n * (n - 1) // 2


def score(articles: list[Article], pred_labels: np.ndarray, labels: LabelSet) -> ScoreResult:
    """예측 군집(pred_labels, articles와 같은 순서)을 정답과 비교한다."""
    if len(articles) != len(pred_labels):
        raise ValueError("articles와 pred_labels 길이가 다릅니다.")

    # 정답이 있는 기사만 채점 대상
    labeled = [
        (a, int(p))
        for a, p in zip(articles, pred_labels, strict=True)
        if labels.issue_of(a.id) is not None
    ]
    n_unlabeled = len(articles) - len(labeled)

    if not labeled:
        return ScoreResult(
            n_labeled=0,
            n_unlabeled=n_unlabeled,
            n_truth_issues=0,
            n_pred_clusters=0,
            ari=0.0,
            pairwise=PairwiseScore(0.0, 0.0, 0.0, 0, 0, 0),
            overmerges=[],
            oversplits=[],
        )

    truth = [labels.issue_of(a.id) for a, _ in labeled]
    pred = [p for _, p in labeled]

    ari = float(adjusted_rand_score(truth, pred))

    # 교차표: (정답 이슈, 예측 묶음) → 기사 수
    contingency: dict[tuple[str, int], int] = {}
    for issue, cluster in zip(truth, pred, strict=True):
        contingency[(issue, cluster)] = contingency.get((issue, cluster), 0) + 1

    truth_sizes: dict[str, int] = {}
    pred_sizes: dict[int, int] = {}
    for (issue, cluster), n in contingency.items():
        truth_sizes[issue] = truth_sizes.get(issue, 0) + n
        pred_sizes[cluster] = pred_sizes.get(cluster, 0) + n

    total_positive = sum(_pairs(n) for n in truth_sizes.values())
    pred_positive = sum(_pairs(n) for n in pred_sizes.values())
    tp = sum(_pairs(n) for n in contingency.values())
    fp = pred_positive - tp
    fn = total_positive - tp

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    pairwise = PairwiseScore(precision, recall, f1, tp, fp, fn)

    # 잘못 합침·잘못 나뉨 사례 (읽기용, 정렬 고정)
    articles_by_id = {a.id: a for a, _ in labeled}
    cluster_to_issue_members: dict[int, dict[str, list[str]]] = {}
    issue_to_cluster_members: dict[str, dict[int, list[str]]] = {}
    for a, cluster in labeled:
        issue = labels.issue_of(a.id)
        cluster_to_issue_members.setdefault(cluster, {}).setdefault(issue, []).append(a.id)
        issue_to_cluster_members.setdefault(issue, {}).setdefault(cluster, []).append(a.id)

    def _render(ids: list[str]) -> list[str]:
        return [_label(articles_by_id[i]) for i in sorted(ids)]

    overmerges = [
        MergeCase(
            pred_cluster=cluster,
            members_by_issue={issue: _render(ids) for issue, ids in sorted(by_issue.items())},
        )
        for cluster, by_issue in sorted(cluster_to_issue_members.items())
        if len(by_issue) >= 2
    ]
    oversplits = [
        SplitCase(
            issue=issue,
            members_by_cluster={
                cluster: _render(ids) for cluster, ids in sorted(by_cluster.items())
            },
        )
        for issue, by_cluster in sorted(issue_to_cluster_members.items())
        if len(by_cluster) >= 2
    ]

    return ScoreResult(
        n_labeled=len(labeled),
        n_unlabeled=n_unlabeled,
        n_truth_issues=len(truth_sizes),
        n_pred_clusters=len(pred_sizes),
        ari=ari,
        pairwise=pairwise,
        overmerges=overmerges,
        oversplits=oversplits,
    )
