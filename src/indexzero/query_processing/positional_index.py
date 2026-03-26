"""Build a positional index for M5 phrase and proximity matching."""

from __future__ import annotations

from collections import defaultdict

from indexzero.text_processing.contracts import TokenizedDocument

from .contracts import PositionalIndex, PositionalPosting


def build_positional_index(documents: list[TokenizedDocument]) -> PositionalIndex:
    positions_by_term: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
    document_lengths: dict[str, int] = {}

    for document in documents:
        document_lengths[document.doc_id] = document.token_count
        for position, term in enumerate(document.tokens):
            positions_by_term[term][document.doc_id].append(position)

    postings: dict[str, list[PositionalPosting]] = {}
    for term, doc_positions in positions_by_term.items():
        postings[term] = sorted(
            [
                PositionalPosting(
                    doc_id=doc_id,
                    term_frequency=len(positions),
                    positions=positions,
                )
                for doc_id, positions in doc_positions.items()
            ],
            key=lambda posting: posting.doc_id,
        )

    return PositionalIndex(
        postings=postings,
        document_lengths=document_lengths,
        document_count=len(documents),
        total_terms=sum(document_lengths.values()),
    )
