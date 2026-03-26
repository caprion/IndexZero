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

import re
import unicodedata
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

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def _strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(
        character for character in normalized if not unicodedata.combining(character)
    )


def _split_numeric_boundaries(text: str) -> str:
    text = re.sub(r"(?<=[A-Za-z])(?=\d)", " ", text)
    text = re.sub(r"(?<=\d)(?=[A-Za-z])", " ", text)
    return text


def _stem_token(token: str) -> str:
    if len(token) <= 3:
        return token
    stem = token
    if token.endswith("ies") and len(token) > 5:
        stem = token[:-3] + "y"
    else:
        for suffix in ("ing", "ers", "er", "ed", "es", "s"):
            if token.endswith(suffix) and len(token) > len(suffix) + 2:
                stem = token[: -len(suffix)]
                break
    if len(stem) >= 2 and stem[-1] == stem[-2]:
        stem = stem[:-1]
    if len(stem) < 3:
        return token
    return stem


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
    config = config or TokenizerConfig()
    normalized = unicodedata.normalize("NFKC", text)
    if config.strip_accents:
        normalized = _strip_accents(normalized)
    if config.lowercase:
        normalized = normalized.lower()
    if config.split_numeric_boundaries:
        normalized = _split_numeric_boundaries(normalized)
    normalized = normalized.replace("&", " and ")
    normalized = re.sub(r"[/|_+()-]+", " ", normalized)
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


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
    config = config or TokenizerConfig()
    normalized = normalize_text(text, config)
    tokens = TOKEN_PATTERN.findall(normalized)

    if config.drop_stopwords:
        tokens = [token for token in tokens if token not in STOPWORDS]

    if config.stemming == "suffix":
        tokens = [_stem_token(token) for token in tokens]
    elif config.stemming != "none":
        raise ValueError(f"Unsupported stemming mode: {config.stemming}")

    return tokens


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
    config = config or TokenizerConfig()
    normalized = normalize_text(text, config)
    tokens = tokenize_text(text, config)
    return TokenizedDocument(
        doc_id=doc_id,
        normalized_text=normalized,
        tokens=tokens,
        term_counts=Counter(tokens),
    )
