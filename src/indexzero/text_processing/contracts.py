"""Data contracts for the text processing pipeline.

These dataclasses define the shapes that flow between modules.
M2 (inverted index) will consume TokenizedDocument and Vocabulary directly.

Students: This file is GIVEN to you. Do not modify it.
"""

# This line lets you write list[str] instead of List[str] on Python 3.9.
# Safe to ignore — it doesn't change how your code runs.
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field


@dataclass(frozen=True)
class TokenizerConfig:
    """Configuration for the text processing pipeline.

    Every flag is a design choice with downstream consequences.
    The decision log asks you to justify each one.
    """

    lowercase: bool = True
    strip_accents: bool = False
    split_numeric_boundaries: bool = False
    drop_stopwords: bool = False
    stemming: str = "none"  # "none" or "suffix"


@dataclass(frozen=True)
class TokenizedDocument:
    """A single document after tokenization.

    Invariants (tested automatically):
    - len(tokens) == sum(term_counts.values())
    - No empty strings in tokens
    - doc_id is preserved from input
    """

    doc_id: str
    normalized_text: str
    tokens: list[str]
    # Counter[str] counts how many times each token appears.
    # Create one from a list: Counter(["a", "b", "a"]) → Counter({"a": 2, "b": 1})
    term_counts: Counter[str]

    # @property makes this accessible as doc.token_count (no parentheses),
    # like a field rather than a method call.
    @property
    def token_count(self) -> int:
        """Total number of tokens emitted for this document."""
        return sum(self.term_counts.values())


@dataclass(frozen=True)
class Vocabulary:
    """Corpus-level token statistics built from a collection of documents.

    Fields:
        token_to_id: Stable mapping from token string to integer ID.
        document_frequency: Number of documents containing each token.
        collection_frequency: Total occurrences of each token across the corpus.
        document_count: Number of documents in the collection.
        total_terms: Sum of all token occurrences across all documents.
    """

    token_to_id: dict[str, int] = field(default_factory=dict)
    document_frequency: dict[str, int] = field(default_factory=dict)
    collection_frequency: dict[str, int] = field(default_factory=dict)
    document_count: int = 0
    total_terms: int = 0
