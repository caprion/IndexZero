"""Tests for M2 bonus: index persistence (save/load round-trip).

These tests only run if save_index and load_index are implemented.
Skip them until you've finished the core (build_index + lookup).

Run with:
    pytest tests/test_index_io.py -v
"""

from __future__ import annotations

import pytest

from indexzero.text_processing import TokenizerConfig, tokenize_document
from indexzero.indexing import build_index, save_index, load_index, lookup


def _m1_implemented() -> bool:
    try:
        tokenize_document("test", "hello world", TokenizerConfig())
        return True
    except NotImplementedError:
        return False


pytestmark = pytest.mark.skipif(
    not _m1_implemented(),
    reason="M1 (text processing) must be implemented before running M2 tests.",
)


@pytest.fixture
def sample_documents():
    config = TokenizerConfig()
    pairs = [
        ("fk-001", "Redmi Note 13 5G Mobile Phone 8GB RAM 256GB Storage"),
        ("fk-002", "Samsung Galaxy M14 5G 6GB RAM 128GB Dark Blue"),
        ("fk-003", "Nike Revolution Running Shoes for Men"),
    ]
    return [tokenize_document(doc_id, text, config) for doc_id, text in pairs]


def _is_implemented(func, *args, **kwargs):
    """Check if a function is implemented (doesn't raise NotImplementedError)."""
    try:
        func(*args, **kwargs)
        return True
    except NotImplementedError:
        return False


class TestIndexRoundTrip:
    """Save/load round-trip tests."""

    def test_round_trip_preserves_document_count(self, sample_documents, tmp_path):
        original = build_index(sample_documents)
        path = tmp_path / "index.json"

        if not _is_implemented(save_index, original, path):
            pytest.skip("save_index not yet implemented")

        save_index(original, path)
        loaded = load_index(path)
        assert loaded.document_count == original.document_count

    def test_round_trip_preserves_total_terms(self, sample_documents, tmp_path):
        original = build_index(sample_documents)
        path = tmp_path / "index.json"

        if not _is_implemented(save_index, original, path):
            pytest.skip("save_index not yet implemented")

        save_index(original, path)
        loaded = load_index(path)
        assert loaded.total_terms == original.total_terms

    def test_round_trip_preserves_document_lengths(self, sample_documents, tmp_path):
        original = build_index(sample_documents)
        path = tmp_path / "index.json"

        if not _is_implemented(save_index, original, path):
            pytest.skip("save_index not yet implemented")

        save_index(original, path)
        loaded = load_index(path)
        assert loaded.document_lengths == original.document_lengths

    def test_round_trip_preserves_postings(self, sample_documents, tmp_path):
        original = build_index(sample_documents)
        path = tmp_path / "index.json"

        if not _is_implemented(save_index, original, path):
            pytest.skip("save_index not yet implemented")

        save_index(original, path)
        loaded = load_index(path)

        assert set(loaded.postings.keys()) == set(original.postings.keys())
        for term in original.postings:
            orig_list = original.postings[term]
            load_list = loaded.postings[term]
            assert len(orig_list) == len(load_list)
            for po, pl in zip(orig_list, load_list):
                assert po.doc_id == pl.doc_id
                assert po.term_frequency == pl.term_frequency

    def test_round_trip_preserves_lookup(self, sample_documents, tmp_path):
        original = build_index(sample_documents)
        path = tmp_path / "index.json"

        if not _is_implemented(save_index, original, path):
            pytest.skip("save_index not yet implemented")

        save_index(original, path)
        loaded = load_index(path)

        for term in original.postings:
            orig_results = lookup(original, term)
            load_results = lookup(loaded, term)
            assert len(orig_results) == len(load_results)

    def test_output_is_valid_json(self, sample_documents, tmp_path):
        """The saved file is valid, human-readable JSON."""
        import json

        original = build_index(sample_documents)
        path = tmp_path / "index.json"

        if not _is_implemented(save_index, original, path):
            pytest.skip("save_index not yet implemented")

        save_index(original, path)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "postings" in data
        assert "document_lengths" in data
