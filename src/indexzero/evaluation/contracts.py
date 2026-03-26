"""Data contracts for the evaluation module (M4).

These dataclasses define the shapes that flow through the evaluation harness.
RelevanceJudgment captures human labels, QueryResults holds ranked output
from M3, and EvalReport aggregates quality metrics across queries.

Students: This file is GIVEN to you. Do not modify it.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RelevanceJudgment:
    """One human relevance label for a (query, document) pair.

    Attributes:
        query_id: Identifier for the query being judged.
        doc_id: Identifier for the document being judged.
        relevance: Integer grade from 0 to 3.
            0 = Irrelevant  — the document has nothing to do with the query.
            1 = Complement   — related but not what the user wants directly.
            2 = Substitute   — a reasonable alternative to the ideal result.
            3 = Exact        — precisely what the user is looking for.
    """

    query_id: str
    doc_id: str
    relevance: int


@dataclass(frozen=True)
class QueryResults:
    """Ranked result list for one query.

    Position 0 is rank 1 (the top result). Evaluation only cares about
    document ORDER, not scores — this is why doc_ids is list[str] rather
    than list[SearchResult].

    Attributes:
        query_id: Identifier for the query that produced these results.
        doc_ids: Ordered list of document identifiers. Position 0 = rank 1.
    """

    query_id: str
    doc_ids: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class QueryMetrics:
    """Per-query evaluation scores.

    Attributes:
        query_id: Identifier for the evaluated query.
        precision_at_k: Fraction of top-k results that are relevant.
        recall_at_k: Fraction of all relevant docs found in top-k.
        reciprocal_rank: 1 / rank of the first relevant result (0 if none).
        ndcg_at_k: Normalized Discounted Cumulative Gain at k.
    """

    query_id: str
    precision_at_k: float
    recall_at_k: float
    reciprocal_rank: float
    ndcg_at_k: float


@dataclass(frozen=True)
class EvalReport:
    """Aggregate evaluation report across all queries.

    Attributes:
        per_query: List of per-query metric breakdowns.
        mean_precision_at_k: Average precision@k across all queries.
        mean_recall_at_k: Average recall@k across all queries.
        mean_reciprocal_rank: Average reciprocal rank (MRR) across all queries.
        mean_ndcg_at_k: Average nDCG@k across all queries.
        k: The cutoff depth used for evaluation.
        num_queries: Total number of queries evaluated.
    """

    per_query: list[QueryMetrics] = field(default_factory=list)
    mean_precision_at_k: float = 0.0
    mean_recall_at_k: float = 0.0
    mean_reciprocal_rank: float = 0.0
    mean_ndcg_at_k: float = 0.0
    k: int = 10
    num_queries: int = 0
