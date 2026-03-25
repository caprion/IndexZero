"""JSON serialization helpers for InvertedIndex.

These are provided so you can focus on building the index, not fighting
Python's json module. Read them -- they show a common pattern for
converting dataclasses to/from JSON-safe dicts.

Students: This file is GIVEN to you. Do not modify it.
"""

from __future__ import annotations

from .contracts import InvertedIndex, Posting


def index_to_dict(index: InvertedIndex) -> dict:
    """Convert an InvertedIndex to a JSON-safe dictionary.

    Posting dataclasses become plain dicts. The average_document_length
    property is included for convenience but is recomputed on load.
    """
    return {
        "document_count": index.document_count,
        "total_terms": index.total_terms,
        "document_lengths": index.document_lengths,
        "postings": {
            term: [
                {"doc_id": p.doc_id, "term_frequency": p.term_frequency}
                for p in posting_list
            ]
            for term, posting_list in index.postings.items()
        },
    }


def index_from_dict(data: dict) -> InvertedIndex:
    """Reconstruct an InvertedIndex from a JSON-parsed dictionary.

    Recomputes average_document_length from document_count and total_terms
    rather than trusting a stored value.
    """
    return InvertedIndex(
        postings={
            term: [
                Posting(
                    doc_id=item["doc_id"],
                    term_frequency=item["term_frequency"],
                )
                for item in posting_list
            ]
            for term, posting_list in data["postings"].items()
        },
        document_lengths=data["document_lengths"],
        document_count=data["document_count"],
        total_terms=data["total_terms"],
    )
