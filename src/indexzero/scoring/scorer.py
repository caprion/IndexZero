"""BM25 scoring and search (M3).

Students: Implement the three functions below in order.

Phase 1 — compute_idf: understand term rarity.
Phase 2 — score_bm25: the full per-term score (IDF + saturation + length norm).
Phase 3 — search: sum per-term scores, rank, return top-k.

Uses natural log (math.log). Negative IDF values are expected for terms
that appear in more than half the corpus — this is correct behavior,
not a bug.
"""

from __future__ import annotations

import math

from ..indexing.contracts import InvertedIndex
from .contracts import ScorerConfig, SearchResult


def compute_idf(term: str, index: InvertedIndex) -> float:
    """Inverse Document Frequency — how rare is this term in the corpus?

    Formula:
        IDF(t) = ln((N - df + 0.5) / (df + 0.5))

    where:
        N  = index.document_count (total documents in corpus)
        df = number of documents containing the term
             (length of the term's posting list)

    Returns:
        The IDF value. Positive for rare terms, negative for very common
        terms (df > N/2). Returns 0.0 if the term is not in the index.

    Example:
        A term in 2 of 500 documents has high IDF (~5.5).
        A term in 400 of 500 documents has negative IDF (~-1.4).
    """
    posting_list = index.postings.get(term, [])
    df = len(posting_list)
    if df == 0:
        return 0.0
    n = index.document_count
    return math.log((n - df + 0.5) / (df + 0.5))


def score_bm25(
    term: str,
    doc_id: str,
    index: InvertedIndex,
    config: ScorerConfig,
) -> float:
    """BM25 relevance score for one term in one document.

    Formula:
        score(t, d) = IDF(t) * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avgdl))

    where:
        tf    = term frequency of t in document d
        dl    = document length (token count) of d
        avgdl = average document length across the corpus
        k1, b = tuning parameters from config

    Returns:
        The BM25 score contribution of this term for this document.
        Returns 0.0 if the term is not in the index, or if doc_id
        does not appear in the term's posting list.

    Invariants:
        - Same tf, shorter document -> higher score (when b > 0).
        - Higher tf -> higher score, but with diminishing returns.
        - b=0 removes all length normalization.
        - k1 controls how quickly tf saturates.
    """
    posting_list = index.postings.get(term, [])
    if not posting_list:
        return 0.0

    tf = 0
    for posting in posting_list:
        if posting.doc_id == doc_id:
            tf = posting.term_frequency
            break

    if tf == 0:
        return 0.0

    dl = index.document_lengths[doc_id]
    avgdl = index.average_document_length
    idf = compute_idf(term, index)

    numerator = tf * (config.k1 + 1)
    denominator = tf + config.k1 * (1 - config.b + config.b * dl / avgdl)

    return idf * numerator / denominator


def search(
    query_terms: list[str],
    index: InvertedIndex,
    config: ScorerConfig,
    top_k: int = 10,
) -> list[SearchResult]:
    """Rank documents for a multi-term query using BM25.

    For each document that contains at least one query term:
        total_score = sum of score_bm25(term, doc_id, index, config)
                      for each term in query_terms

    Return the top_k documents sorted by:
        1. score descending (highest first)
        2. doc_id ascending (alphabetical tie-break)

    Args:
        query_terms: Pre-tokenized query terms (already lowercased).
            Duplicate terms are scored once per occurrence — if the
            caller passes ["samsung", "samsung"], samsung counts twice.
        index: The inverted index built in M2.
        config: BM25 parameters (k1, b).
        top_k: Maximum number of results to return.

    Returns:
        A list of SearchResult(doc_id, score), length <= top_k.
        Empty list if no documents match any query term.
    """
    scores: dict[str, float] = {}

    for term in query_terms:
        posting_list = index.postings.get(term, [])
        for posting in posting_list:
            doc_id = posting.doc_id
            score = score_bm25(term, doc_id, index, config)
            scores[doc_id] = scores.get(doc_id, 0.0) + score

    ranked = sorted(scores.items(), key=lambda pair: (-pair[1], pair[0]))
    return [SearchResult(doc_id=doc_id, score=score) for doc_id, score in ranked[:top_k]]
