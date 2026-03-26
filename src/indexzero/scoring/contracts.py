"""Data contracts for the scoring module (M3).

These dataclasses define the shapes that flow between M3 and downstream modules.
M4 (Evaluation) converts SearchResult lists into QueryResults for evaluation.

Students: This file is GIVEN to you. Do not modify it.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScorerConfig:
    """BM25 tuning parameters.

    Attributes:
        k1: Controls term-frequency saturation. Higher k1 means repeated
            mentions keep mattering longer. At k1=0, BM25 ignores tf entirely
            and behaves like binary term matching weighted by IDF.
        b: Controls length normalization. b=1.0 fully normalizes for document
            length. b=0.0 ignores length differences entirely.
    """

    k1: float = 1.2
    b: float = 0.75


@dataclass(frozen=True)
class SearchResult:
    """A single scored document in a ranked result list.

    Attributes:
        doc_id: The document identifier (matches Posting.doc_id from M2).
        score: The BM25 relevance score. Higher is more relevant.
            Can be negative if the query contains very common terms.
    """

    doc_id: str
    score: float
