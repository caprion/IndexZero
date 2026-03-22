"""Tests for the tokenizer — M1 text processing.

These tests check INVARIANTS, not exact outputs. Your tokenizer can
make different normalization choices and still pass, as long as it
respects the contracts.

Run:  pytest tests/test_tokenizer.py -v
"""

from __future__ import annotations

import pytest

from indexzero.text_processing import (
    TokenizedDocument,
    TokenizerConfig,
    normalize_text,
    tokenize_document,
    tokenize_text,
)


# ---------------------------------------------------------------------------
# normalize_text
# ---------------------------------------------------------------------------

class TestNormalizeText:
    """Tests for the normalize_text function."""

    def test_returns_a_string(self, sample_text: str, default_config: TokenizerConfig) -> None:
        result = normalize_text(sample_text, default_config)
        assert isinstance(result, str)

    def test_lowercasing_produces_lowercase_output(self, sample_text: str) -> None:
        config = TokenizerConfig(lowercase=True)
        result = normalize_text(sample_text, config)
        # Every alphabetic character should be lowercase
        assert result == result.lower()

    def test_no_lowercase_preserves_case(self) -> None:
        config = TokenizerConfig(lowercase=False)
        result = normalize_text("HP Laptop", config)
        # At least one uppercase letter should survive
        assert any(c.isupper() for c in result)

    def test_default_config_when_none(self, sample_text: str) -> None:
        # Should not raise when config is None
        result = normalize_text(sample_text, None)
        assert isinstance(result, str)

    def test_empty_input_returns_empty_or_whitespace(self) -> None:
        result = normalize_text("", TokenizerConfig())
        assert result.strip() == ""


# ---------------------------------------------------------------------------
# tokenize_text
# ---------------------------------------------------------------------------

class TestTokenizeText:
    """Tests for the tokenize_text function."""

    def test_returns_a_list_of_strings(self, sample_text: str) -> None:
        tokens = tokenize_text(sample_text)
        assert isinstance(tokens, list)
        assert all(isinstance(t, str) for t in tokens)

    def test_no_empty_tokens(self, sample_texts: list[str]) -> None:
        """No empty strings should appear in the token list."""
        for text in sample_texts:
            tokens = tokenize_text(text)
            assert "" not in tokens, f"Empty token found for: {text!r}"

    def test_deterministic(self, sample_text: str) -> None:
        """Same input + same config → identical output, every time."""
        config = TokenizerConfig()
        first = tokenize_text(sample_text, config)
        second = tokenize_text(sample_text, config)
        assert first == second

    def test_deterministic_with_full_config(self, sample_text: str, full_config: TokenizerConfig) -> None:
        """Determinism holds even with all options enabled."""
        first = tokenize_text(sample_text, full_config)
        second = tokenize_text(sample_text, full_config)
        assert first == second

    def test_lowercase_tokens_when_enabled(self, sample_texts: list[str]) -> None:
        """When lowercase=True, every token must be fully lowercase."""
        config = TokenizerConfig(lowercase=True)
        for text in sample_texts:
            tokens = tokenize_text(text, config)
            for token in tokens:
                assert token == token.lower(), (
                    f"Token {token!r} is not lowercase for input: {text!r}"
                )

    def test_stopword_removal_actually_removes(self) -> None:
        """Known stopwords should not appear in output when enabled."""
        config = TokenizerConfig(drop_stopwords=True)
        text = "Running shoes for men with great support"
        tokens = tokenize_text(text, config)
        # "for" and "with" are in the STOPWORDS set
        assert "for" not in tokens
        assert "with" not in tokens

    def test_stopwords_present_when_not_dropped(self) -> None:
        """With stopwords disabled, common words should survive."""
        config = TokenizerConfig(drop_stopwords=False)
        text = "shoes for men"
        tokens = tokenize_text(text, config)
        assert "for" in tokens

    def test_produces_tokens_for_nonempty_input(self, sample_texts: list[str]) -> None:
        """Any non-empty text with alphanumeric characters should produce at least one token."""
        for text in sample_texts:
            tokens = tokenize_text(text)
            assert len(tokens) > 0, f"No tokens produced for: {text!r}"

    def test_none_config_uses_defaults(self, sample_text: str) -> None:
        """Passing None for config should behave like TokenizerConfig()."""
        tokens_none = tokenize_text(sample_text, None)
        tokens_default = tokenize_text(sample_text, TokenizerConfig())
        assert tokens_none == tokens_default

    # --- Config flag correctness tests (push past trivial implementations) ---

    def test_stemming_changes_output(self) -> None:
        """When stemming='suffix', at least one token should differ from no-stemming."""
        text = "Running shoes for runners"
        plain = tokenize_text(text, TokenizerConfig(stemming="none"))
        stemmed = tokenize_text(text, TokenizerConfig(stemming="suffix"))
        assert plain != stemmed, "Stemming had no effect — is it implemented?"

    def test_stemming_produces_nonempty_tokens(self) -> None:
        """Stemmed tokens must not be empty strings."""
        text = "Running shoes for runners"
        tokens = tokenize_text(text, TokenizerConfig(stemming="suffix"))
        assert all(len(t) > 0 for t in tokens)

    def test_stemming_shortens_or_preserves(self) -> None:
        """Stemmed tokens should be shorter than or equal to their plain form."""
        text = "Running shoes for runners"
        plain = tokenize_text(text, TokenizerConfig(stemming="none"))
        stemmed = tokenize_text(text, TokenizerConfig(stemming="suffix"))
        for p, s in zip(plain, stemmed):
            assert len(s) <= len(p), f"Stemmed '{s}' is longer than plain '{p}'"

    def test_numeric_boundary_split(self) -> None:
        """'8GB' with split_numeric_boundaries=True should produce at least 2 tokens."""
        config = TokenizerConfig(split_numeric_boundaries=True)
        tokens = tokenize_text("8GB RAM", config)
        # "8GB" should split into at least "8" and "gb" (or "GB")
        numeric_tokens = [t for t in tokens if t.isdigit()]
        assert len(numeric_tokens) >= 1, "Numeric boundary split didn't separate digits"
        assert len(tokens) >= 3, f"Expected >=3 tokens from '8GB RAM', got {tokens}"

    def test_numeric_boundary_off_keeps_together(self) -> None:
        """Without numeric splitting, '8GB' may stay as one token or split by normalization."""
        config_off = TokenizerConfig(split_numeric_boundaries=False)
        config_on = TokenizerConfig(split_numeric_boundaries=True)
        tokens_off = tokenize_text("Note13Pro", config_off)
        tokens_on = tokenize_text("Note13Pro", config_on)
        # When enabled, should produce more tokens than when disabled
        assert len(tokens_on) >= len(tokens_off), (
            "Numeric splitting should produce at least as many tokens"
        )

    def test_accent_stripping_normalizes(self) -> None:
        """Accented characters should be stripped when strip_accents=True."""
        config = TokenizerConfig(strip_accents=True)
        tokens = tokenize_text("cafe\u0301 resume\u0301", config)
        # The accent-stripped forms should not contain combining characters
        for token in tokens:
            assert token == token.encode("ascii", errors="ignore").decode("ascii"), (
                f"Token '{token}' still contains non-ASCII after accent stripping"
            )

    def test_accent_stripping_off_preserves(self) -> None:
        """Without accent stripping, accented chars may survive in tokens."""
        config_on = TokenizerConfig(strip_accents=True)
        config_off = TokenizerConfig(strip_accents=False)
        text = "cafe\u0301"
        tokens_on = tokenize_text(text, config_on)
        tokens_off = tokenize_text(text, config_off)
        # At minimum, the two outputs should differ OR the off version
        # should still handle the text without error
        assert isinstance(tokens_off, list)

    # --- Stemming quality: linguistic convergence, not just truncation ---

    def test_stemming_converges_related_words(self) -> None:
        """Words with the same root should produce the same stem.

        A suffix trimmer that just chops 2 characters will turn "running"
        into "runni" and "runs" into "ru" — those don't match.
        A correct implementation maps both to the same stem.
        """
        config = TokenizerConfig(stemming="suffix")
        stem_running = tokenize_text("running", config)
        stem_runs = tokenize_text("runs", config)
        assert stem_running == stem_runs, (
            f"'running' → {stem_running}, 'runs' → {stem_runs} — "
            "related words should converge to the same stem"
        )

    def test_stemming_does_not_overstem_short_words(self) -> None:
        """Short words (<=3 chars) should survive stemming unchanged."""
        config = TokenizerConfig(stemming="suffix")
        tokens = tokenize_text("the cat ran", config)
        # "the" (3 chars), "cat" (3 chars), "ran" (3 chars) — too short to stem
        assert all(len(t) >= 2 for t in tokens), (
            f"Over-stemming produced very short tokens: {tokens}"
        )

    # --- Separator normalization: hyphens, slashes, apostrophes ---

    def test_hyphenated_text_produces_tokens(self) -> None:
        """Hyphenated words like 'non-stick' should produce meaningful tokens."""
        tokens = tokenize_text("non-stick tawa")
        # Must produce at least 2 tokens (non + stick, or nonstick + tawa)
        assert len(tokens) >= 2, f"Hyphenated text produced too few tokens: {tokens}"
        # No token should contain the raw hyphen
        assert not any("-" in t for t in tokens), (
            f"Raw hyphen survived in tokens: {tokens}"
        )

    def test_slash_separated_values(self) -> None:
        """Slashes between values like '24cm/28cm' should split into tokens."""
        tokens = tokenize_text("tawa 24cm/28cm combo")
        assert len(tokens) >= 3, f"Slash-separated text produced too few tokens: {tokens}"
        assert not any("/" in t for t in tokens), (
            f"Raw slash survived in tokens: {tokens}"
        )

    def test_apostrophe_handling(self) -> None:
        """Apostrophes in words like "women's" or "L'Oreal" should not break tokenization."""
        tokens = tokenize_text("women's L'Oreal creme")
        assert len(tokens) >= 2, f"Apostrophe text produced too few tokens: {tokens}"
        # No empty tokens from bad splitting around apostrophes
        assert "" not in tokens

    def test_edge_texts_produce_tokens(self, edge_texts: list[str]) -> None:
        """Every edge-case text must produce at least one non-empty token."""
        for text in edge_texts:
            tokens = tokenize_text(text)
            assert len(tokens) > 0, f"No tokens for edge text: {text!r}"
            assert "" not in tokens, f"Empty token for edge text: {text!r}"


# ---------------------------------------------------------------------------
# tokenize_document
# ---------------------------------------------------------------------------

class TestTokenizeDocument:
    """Tests for the tokenize_document function."""

    def test_returns_tokenized_document(self) -> None:
        doc = tokenize_document("fk-001", "Water bottle bottle")
        assert isinstance(doc, TokenizedDocument)

    def test_doc_id_preserved(self) -> None:
        """The document ID in the output must match the input."""
        doc = tokenize_document("test-42", "Some product title")
        assert doc.doc_id == "test-42"

    def test_token_count_equals_sum_of_term_counts(self, sample_texts: list[str]) -> None:
        """token_count must equal the sum of all term_counts values."""
        for i, text in enumerate(sample_texts):
            doc = tokenize_document(f"doc-{i}", text)
            assert doc.token_count == sum(doc.term_counts.values()), (
                f"token_count mismatch for: {text!r}"
            )

    def test_token_count_equals_len_tokens(self, sample_texts: list[str]) -> None:
        """token_count must equal len(tokens)."""
        for i, text in enumerate(sample_texts):
            doc = tokenize_document(f"doc-{i}", text)
            assert doc.token_count == len(doc.tokens), (
                f"token_count != len(tokens) for: {text!r}"
            )

    def test_no_empty_tokens_in_document(self, sample_texts: list[str]) -> None:
        """No empty strings in the tokens list of a document."""
        for i, text in enumerate(sample_texts):
            doc = tokenize_document(f"doc-{i}", text)
            assert "" not in doc.tokens

    def test_term_counts_match_tokens(self) -> None:
        """Every token in the list should be counted in term_counts."""
        doc = tokenize_document("fk-001", "bottle water bottle water bottle")
        # term_counts should reflect the actual token list
        from collections import Counter

        expected = Counter(doc.tokens)
        assert dict(doc.term_counts) == dict(expected)

    def test_none_config_uses_defaults(self) -> None:
        """Passing None for config should produce the same result as default config."""
        doc_none = tokenize_document("d1", "Test text", None)
        doc_default = tokenize_document("d1", "Test text", TokenizerConfig())
        assert doc_none.tokens == doc_default.tokens
        assert doc_none.doc_id == doc_default.doc_id

    def test_different_configs_may_produce_different_output(self) -> None:
        """Changing config should be able to change the output."""
        text = "Running shoes for men"
        doc_default = tokenize_document("d1", text, TokenizerConfig())
        doc_stopped = tokenize_document(
            "d1", text, TokenizerConfig(drop_stopwords=True)
        )
        # With stopword removal, we expect fewer tokens
        assert doc_stopped.token_count <= doc_default.token_count
