"""Tests for the vocabulary builder — M1 text processing.

These tests check INVARIANTS, not exact stems or specific token strings.
Your vocabulary builder should work correctly regardless of which
stemming or normalization choices you made in the tokenizer.

Run:  pytest tests/test_vocabulary.py -v
"""

from __future__ import annotations

import pytest

from indexzero.text_processing import (
    TokenizerConfig,
    Vocabulary,
    build_vocabulary,
    tokenize_document,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_documents(
    texts: list[tuple[str, str]],
    config: TokenizerConfig | None = None,
):
    """Create a list of TokenizedDocuments from (doc_id, text) pairs."""
    return [tokenize_document(doc_id, text, config) for doc_id, text in texts]


# ---------------------------------------------------------------------------
# build_vocabulary
# ---------------------------------------------------------------------------

class TestBuildVocabulary:
    """Tests for the build_vocabulary function."""

    def test_returns_vocabulary_type(self) -> None:
        docs = _make_documents([("d1", "hello world")])
        vocab = build_vocabulary(docs)
        assert isinstance(vocab, Vocabulary)

    def test_document_count_matches(self) -> None:
        docs = _make_documents([
            ("d1", "hello world"),
            ("d2", "world peace"),
            ("d3", "hello peace love"),
        ])
        vocab = build_vocabulary(docs)
        assert vocab.document_count == 3

    def test_total_terms_equals_sum_of_all_tokens(self) -> None:
        """total_terms should be the sum of token counts across all documents."""
        docs = _make_documents([
            ("d1", "apple banana apple"),
            ("d2", "banana cherry"),
        ])
        vocab = build_vocabulary(docs)
        expected_total = sum(doc.token_count for doc in docs)
        assert vocab.total_terms == expected_total

    def test_every_token_has_an_id(self) -> None:
        """Every token from any document must appear in token_to_id."""
        docs = _make_documents([
            ("d1", "alpha beta gamma"),
            ("d2", "delta epsilon"),
        ])
        vocab = build_vocabulary(docs)
        all_tokens = set()
        for doc in docs:
            all_tokens.update(doc.tokens)
        for token in all_tokens:
            assert token in vocab.token_to_id, f"Missing token_to_id entry: {token!r}"

    def test_document_frequency_does_not_exceed_document_count(self) -> None:
        """No token can appear in more documents than exist."""
        docs = _make_documents([
            ("d1", "common rare1"),
            ("d2", "common rare2"),
            ("d3", "common rare3"),
        ])
        vocab = build_vocabulary(docs)
        for token, df in vocab.document_frequency.items():
            assert df <= vocab.document_count, (
                f"df({token!r})={df} exceeds document_count={vocab.document_count}"
            )

    def test_document_frequency_counts_documents_not_occurrences(self) -> None:
        """A token appearing 5 times in one document still has df=1."""
        docs = _make_documents([
            ("d1", "bottle bottle bottle bottle bottle"),
        ])
        vocab = build_vocabulary(docs)
        # Find the token for "bottle" (may be stemmed, so check all tokens)
        for token, df in vocab.document_frequency.items():
            assert df == 1  # Only one document

    def test_collection_frequency_counts_total_occurrences(self) -> None:
        """collection_frequency should count every occurrence, not just unique ones."""
        docs = _make_documents([
            ("d1", "apple apple apple"),
            ("d2", "apple banana"),
        ])
        vocab = build_vocabulary(docs)
        # Total tokens across docs
        total_cf = sum(vocab.collection_frequency.values())
        assert total_cf == vocab.total_terms

    def test_token_ids_are_unique(self) -> None:
        """All assigned token IDs must be unique."""
        docs = _make_documents([
            ("d1", "one two three four five"),
            ("d2", "six seven eight nine ten"),
        ])
        vocab = build_vocabulary(docs)
        ids = list(vocab.token_to_id.values())
        assert len(ids) == len(set(ids)), "Duplicate token IDs found"

    def test_empty_corpus(self) -> None:
        """An empty document list should produce an empty vocabulary."""
        vocab = build_vocabulary([])
        assert vocab.document_count == 0
        assert vocab.total_terms == 0
        assert len(vocab.token_to_id) == 0
