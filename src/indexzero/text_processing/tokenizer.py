"""Tokenizer — the core of M1.

Students implement three functions here:
    1. normalize_text  — clean and normalize a raw string
    2. tokenize_text   — turn a string into a list of tokens
    3. tokenize_document — wrap tokenization with document metadata

Each function has a docstring explaining what it should do and what
invariants the tests check. Start with the simplest version that could
work (split on whitespace, lowercase), then improve iteratively.

Run tests as you go:
    pytest tests/test_tokenizer.py -v
"""

# This line lets you write list[str] instead of List[str] on Python 3.9.
from __future__ import annotations

from collections import Counter

# The dot in ".contracts" means "from this same package."
# Don't run this file directly — use pytest or python -m indexzero.
from .contracts import TokenizedDocument, TokenizerConfig


# A small set of English stopwords. Extend if you want.
STOPWORDS: set[str] = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "he",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "was",
    "were",
    "will",
    "with",
}


def normalize_text(text: str, config: TokenizerConfig | None = None) -> str:
    """Normalize raw text before tokenization.

    This function should apply transformations such as:
    - Unicode normalization (NFKC) — see hints/hint_5 if unfamiliar
    - Lowercasing (if config.lowercase is True)
    - Accent stripping (if config.strip_accents is True)
    - Numeric boundary splitting (if config.split_numeric_boundaries is True)
    - Separator normalization (slashes, hyphens, underscores → spaces)
    - Whitespace collapsing

    If you get stuck on any step, check modules/m1_text_processing/hints/.

    The output should be a clean string ready for splitting into tokens.

    Args:
        text: Raw input string.
        config: Tokenizer configuration. Uses defaults if None.

    Returns:
        A normalized string.
    """
    raise NotImplementedError("Students implement this in M1.")


def tokenize_text(text: str, config: TokenizerConfig | None = None) -> list[str]:
    """Tokenize a string into a list of tokens.

    This function should:
    1. Call normalize_text to clean the input.
    2. Split the normalized text into tokens (e.g., using a regex or split).
    3. Apply stopword removal if config.drop_stopwords is True.
    4. Apply stemming if config.stemming != "none".
       Suffix stemming: strip common endings (-ing, -ed, -er, -s, -ly)
       to group word variants. See hints/hint_3 if your stems don't converge.

    Invariants (tested automatically):
    - No empty strings in the output list.
    - Same input + same config → same output (deterministic).
    - If config.lowercase is True, all tokens are lowercase.

    Args:
        text: Raw input string.
        config: Tokenizer configuration. Uses defaults if None.

    Returns:
        An ordered list of token strings.
    """
    raise NotImplementedError("Students implement this in M1.")


def tokenize_document(
    doc_id: str,
    text: str,
    config: TokenizerConfig | None = None,
) -> TokenizedDocument:
    """Tokenize a document and wrap the result with metadata.

    This function should:
    1. Normalize the text.
    2. Tokenize it.
    3. Count term frequencies.
    4. Return a TokenizedDocument with all fields populated.

    Invariants (tested automatically):
    - doc_id in the output matches the doc_id argument.
    - token_count == sum(term_counts.values())
    - tokens list matches the keys/counts in term_counts.

    Args:
        doc_id: Stable document identifier (e.g., "fk-001").
        text: Raw text to tokenize.
        config: Tokenizer configuration. Uses defaults if None.

    Returns:
        A TokenizedDocument instance.
    """
    raise NotImplementedError("Students implement this in M1.")
