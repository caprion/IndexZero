"""Contracts for the M5 query language."""

from __future__ import annotations

from dataclasses import dataclass


class QueryParseError(ValueError):
    """Raised when a structured query cannot be parsed."""


@dataclass(frozen=True)
class TermNode:
    term: str


@dataclass(frozen=True)
class PhraseNode:
    terms: tuple[str, ...]


@dataclass(frozen=True)
class NearNode:
    left_term: str
    right_term: str
    distance: int


@dataclass(frozen=True)
class AndNode:
    left: "QueryNode"
    right: "QueryNode"


@dataclass(frozen=True)
class OrNode:
    left: "QueryNode"
    right: "QueryNode"


@dataclass(frozen=True)
class NotNode:
    child: "QueryNode"


QueryNode = TermNode | PhraseNode | NearNode | AndNode | OrNode | NotNode
