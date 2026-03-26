"""M4: Evaluation — search quality metrics and harness.

Public API:
    RelevanceJudgment — one human relevance label (query, doc, grade).
    QueryResults      — ranked result list for one query.
    QueryMetrics      — per-query scores (P@k, R@k, MRR, nDCG@k).
    EvalReport        — aggregate metrics across all queries.
    precision_at_k    — fraction of top-k that are relevant.
    recall_at_k       — fraction of all relevant found in top-k.
    reciprocal_rank   — 1 / rank of first relevant result.
    ndcg_at_k         — Normalized Discounted Cumulative Gain at k.
    evaluate          — full evaluation across multiple queries.
    load_qrels        — load relevance judgments from CSV.
    save_qrels        — save relevance judgments to CSV.
"""

from .contracts import EvalReport, QueryMetrics, QueryResults, RelevanceJudgment
from .metrics import evaluate, ndcg_at_k, precision_at_k, recall_at_k, reciprocal_rank
from .qrels_io import load_qrels, save_qrels

__all__ = [
    "EvalReport",
    "QueryMetrics",
    "QueryResults",
    "RelevanceJudgment",
    "evaluate",
    "load_qrels",
    "ndcg_at_k",
    "precision_at_k",
    "recall_at_k",
    "reciprocal_rank",
    "save_qrels",
]
