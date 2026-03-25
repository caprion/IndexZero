"""Public API for the indexing package (M2).

All names here are importable as:
    from indexzero.indexing import InvertedIndex, build_index, ...
"""

from .contracts import InvertedIndex, Posting
from .indexer import build_index, load_index, lookup, save_index

__all__ = [
    "InvertedIndex",
    "Posting",
    "build_index",
    "load_index",
    "lookup",
    "save_index",
]
