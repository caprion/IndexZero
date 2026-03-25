"""M3: BM25 scoring and ranked search.

Public API:
    ScorerConfig    — BM25 tuning parameters (k1, b).
    SearchResult    — A scored document in a ranked list.
    compute_idf     — Inverse Document Frequency for a term.
    score_bm25      — BM25 score for one term in one document.
    search          — Rank documents for a multi-term query.
"""

from .contracts import ScorerConfig, SearchResult
from .scorer import compute_idf, score_bm25, search

__all__ = [
    "ScorerConfig",
    "SearchResult",
    "compute_idf",
    "score_bm25",
    "search",
]
