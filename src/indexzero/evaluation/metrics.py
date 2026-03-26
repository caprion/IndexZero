"""Search quality metrics (M4).

Students: Implement the five functions below in order.

Phase 1 — precision_at_k and recall_at_k: count relevant docs in top-k.
Phase 2 — reciprocal_rank: find the first relevant result.
Phase 3 — ndcg_at_k: position-aware scoring with discounted gain.
Phase 4 — evaluate: orchestrate all metrics across multiple queries.

Uses math.log2 for the nDCG discount. All metrics operate on document
order (rank lists), not on scores — evaluation is score-agnostic.
"""

from __future__ import annotations

import math
from collections import defaultdict

from .contracts import EvalReport, QueryMetrics, QueryResults, RelevanceJudgment


def precision_at_k(
    results: QueryResults,
    judgments: list[RelevanceJudgment],
    k: int = 10,
    relevance_threshold: int = 2,
) -> float:
    """Fraction of top-k results that are relevant.

    Formula:
        P@k = |{relevant docs in top k}| / k

    A document is considered relevant if its relevance grade in the
    judgments is >= relevance_threshold. Documents not present in the
    judgments are treated as grade 0 (not relevant).

    Args:
        results: Ranked result list for one query.
        judgments: Relevance judgments for the same query.
        k: Cutoff depth (must be >= 1). Divides by k even if fewer results exist.
        relevance_threshold: Minimum grade to count as relevant (default 2).

    Returns:
        float in [0.0, 1.0].

    Example:
        Top-3 results are [relevant, irrelevant, relevant] -> P@3 = 2/3.
    """
    if k < 1:
        raise ValueError(f"k must be >= 1, got {k}")
    relevant_docs = {
        judgment.doc_id
        for judgment in judgments
        if judgment.relevance >= relevance_threshold
    }
    top_k = results.doc_ids[:k]
    relevant_in_top_k = sum(1 for doc_id in top_k if doc_id in relevant_docs)
    return relevant_in_top_k / k


def recall_at_k(
    results: QueryResults,
    judgments: list[RelevanceJudgment],
    k: int = 10,
    relevance_threshold: int = 2,
) -> float:
    """Fraction of all relevant documents found in top-k.

    Formula:
        R@k = |{relevant docs in top k}| / |{all relevant docs in qrels}|

    Returns 1.0 if no relevant documents exist in the judgments
    (vacuously true — you cannot miss what does not exist).

    Args:
        results: Ranked result list for one query.
        judgments: Relevance judgments for the same query.
        k: Cutoff depth.
        relevance_threshold: Minimum grade to count as relevant (default 2).

    Returns:
        float in [0.0, 1.0].

    Example:
        2 relevant docs in qrels, 1 found in top-5 -> R@5 = 0.5.
    """
    relevant_docs = {
        judgment.doc_id
        for judgment in judgments
        if judgment.relevance >= relevance_threshold
    }
    total_relevant = len(relevant_docs)
    if total_relevant == 0:
        return 1.0
    top_k = results.doc_ids[:k]
    found = sum(1 for doc_id in top_k if doc_id in relevant_docs)
    return found / total_relevant


def reciprocal_rank(
    results: QueryResults,
    judgments: list[RelevanceJudgment],
    relevance_threshold: int = 2,
) -> float:
    """Reciprocal of the rank of the first relevant result.

    Rank is 1-indexed: the first result has rank 1, the second has rank 2,
    and so on. If no relevant result is found, returns 0.0.

    Only the FIRST relevant result matters — additional relevant results
    at lower ranks do not change the score.

    Args:
        results: Ranked result list for one query.
        judgments: Relevance judgments for the same query.
        relevance_threshold: Minimum grade to count as relevant (default 2).

    Returns:
        float in [0.0, 1.0]. 1.0 means the first result is relevant.
        1/3 means the third result is the first relevant one.
        0.0 means no relevant result was found.
    """
    relevant_docs = {
        judgment.doc_id
        for judgment in judgments
        if judgment.relevance >= relevance_threshold
    }
    for rank, doc_id in enumerate(results.doc_ids, start=1):
        if doc_id in relevant_docs:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(
    results: QueryResults,
    judgments: list[RelevanceJudgment],
    k: int = 10,
) -> float:
    """Normalized Discounted Cumulative Gain at k.

    Unlike precision and recall which treat relevance as binary,
    nDCG uses the full graded relevance scale. Higher grades at
    earlier positions contribute more to the score.

    Formula (1-indexed):
        DCG@k  = sum(i=1..k) rel_i / log2(i + 1)
        IDCG@k = DCG of the ideal ranking (sort all judgment grades
                 descending, take top k)
        nDCG@k = DCG@k / IDCG@k

    Python note: if you use ``enumerate(top_k)`` where i starts at 0,
    the denominator becomes ``math.log2(i + 2)`` (not ``i + 1``).

    Uses LINEAR gain (raw relevance grade), not exponential (2^rel - 1).

    Returns 0.0 if IDCG is 0 (no relevant documents in judgments).

    Args:
        results: Ranked result list for one query.
        judgments: Relevance judgments for the same query.
        k: Cutoff depth.

    Returns:
        float in [0.0, 1.0]. 1.0 means the ranking is ideal.
    """
    grade_map = {judgment.doc_id: judgment.relevance for judgment in judgments}

    dcg = 0.0
    for index, doc_id in enumerate(results.doc_ids[:k]):
        relevance = grade_map.get(doc_id, 0)
        dcg += relevance / math.log2(index + 2)

    ideal_top_k = sorted(
        (judgment.relevance for judgment in judgments),
        reverse=True,
    )[:k]
    idcg = 0.0
    for index, relevance in enumerate(ideal_top_k):
        idcg += relevance / math.log2(index + 2)

    if idcg == 0.0:
        return 0.0
    return dcg / idcg


def evaluate(
    all_results: list[QueryResults],
    all_judgments: list[RelevanceJudgment],
    k: int = 10,
    relevance_threshold: int = 2,
) -> EvalReport:
    """Run full evaluation across multiple queries.

    Groups judgments by query_id, computes per-query metrics for each
    QueryResults, then averages across queries in all_results.

    Queries in all_results with no matching judgments are evaluated
    against an empty judgment list (all docs treated as unjudged).
    The average is computed over all queries in all_results.

    Tip: use ``collections.defaultdict(list)`` to group judgments.

    Args:
        all_results: Ranked result lists, one per query.
        all_judgments: All relevance judgments (mixed across queries).
        k: Cutoff depth for P@k, R@k, and nDCG@k.
        relevance_threshold: Minimum grade for binary relevance metrics.

    Returns:
        EvalReport with per-query breakdowns and mean scores.
    """
    judgments_by_query: dict[str, list[RelevanceJudgment]] = defaultdict(list)
    for judgment in all_judgments:
        judgments_by_query[judgment.query_id].append(judgment)

    per_query: list[QueryMetrics] = []
    for query_results in all_results:
        query_judgments = judgments_by_query.get(query_results.query_id, [])
        per_query.append(
            QueryMetrics(
                query_id=query_results.query_id,
                precision_at_k=precision_at_k(
                    query_results,
                    query_judgments,
                    k,
                    relevance_threshold,
                ),
                recall_at_k=recall_at_k(
                    query_results,
                    query_judgments,
                    k,
                    relevance_threshold,
                ),
                reciprocal_rank=reciprocal_rank(
                    query_results,
                    query_judgments,
                    relevance_threshold,
                ),
                ndcg_at_k=ndcg_at_k(query_results, query_judgments, k),
            )
        )

    num_queries = len(per_query)
    if num_queries == 0:
        return EvalReport(k=k, num_queries=0)

    return EvalReport(
        per_query=per_query,
        mean_precision_at_k=sum(item.precision_at_k for item in per_query) / num_queries,
        mean_recall_at_k=sum(item.recall_at_k for item in per_query) / num_queries,
        mean_reciprocal_rank=sum(item.reciprocal_rank for item in per_query) / num_queries,
        mean_ndcg_at_k=sum(item.ndcg_at_k for item in per_query) / num_queries,
        k=k,
        num_queries=num_queries,
    )
