"""Data contracts for the indexing module (M2).

These dataclasses define the shapes that flow between M2 and downstream modules.
M3 (BM25 ranking) consumes InvertedIndex directly.

Students: This file is GIVEN to you. Do not modify it.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Posting:
    """A single entry in a posting list: one term in one document.

    Attributes:
        doc_id: The document this posting refers to.
        term_frequency: How many times the term appears in this document.
    """

    doc_id: str
    term_frequency: int


@dataclass(frozen=True)
class InvertedIndex:
    """A built inverted index. Treat as read-only after construction.

    Maps each term to its posting list (which documents contain it and how
    often). Also stores document lengths needed for BM25 length normalization.

    Note:
        frozen=True prevents reassigning fields, but nested dict/list values
        are still technically mutable. Don't mutate them -- build a new index
        instead.

    Fields:
        postings: Mapping from term string to list of Posting objects.
        document_lengths: Mapping from doc_id to token count for that document.
        document_count: Number of documents in the index.
        total_terms: Sum of all token counts across all documents.
    """

    postings: dict[str, list[Posting]] = field(default_factory=dict)
    document_lengths: dict[str, int] = field(default_factory=dict)
    document_count: int = 0
    total_terms: int = 0

    @property
    def average_document_length(self) -> float:
        """Mean document length across the indexed collection.

        Derived from total_terms and document_count. Used by BM25 for
        length normalization. Returns 0.0 for an empty index.
        """
        if self.document_count == 0:
            return 0.0
        return self.total_terms / self.document_count
