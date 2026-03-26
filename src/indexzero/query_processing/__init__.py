"""Public API for M5 query execution."""

from .contracts import PositionalIndex, PositionalPosting
from .executor import extract_query_terms, match_near, match_phrase, retrieve, search_structured
from .positional_index import build_positional_index

__all__ = [
    "PositionalIndex",
    "PositionalPosting",
    "build_positional_index",
    "extract_query_terms",
    "match_near",
    "match_phrase",
    "retrieve",
    "search_structured",
]
