"""Contracts for M5 positional indexing."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PositionalPosting:
    doc_id: str
    term_frequency: int
    positions: list[int]


@dataclass(frozen=True)
class PositionalIndex:
    postings: dict[str, list[PositionalPosting]] = field(default_factory=dict)
    document_lengths: dict[str, int] = field(default_factory=dict)
    document_count: int = 0
    total_terms: int = 0
