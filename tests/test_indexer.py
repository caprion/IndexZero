"""Tests for M2: Inverted Index.

These tests check invariants, not exact outputs. Your index must satisfy
structural properties regardless of implementation details.

Run with:
    pytest tests/test_indexer.py -v
"""

from __future__ import annotations

import pytest

from indexzero.text_processing import TokenizerConfig, tokenize_document
from indexzero.indexing import InvertedIndex, Posting, build_index, lookup


def _m1_implemented() -> bool:
    """Check if M1 tokenizer is implemented (not still a stub)."""
    try:
        tokenize_document("test", "hello world", TokenizerConfig())
        return True
    except NotImplementedError:
        return False


# Skip all M2 tests if M1 isn't implemented yet.
# Students working on M1 shouldn't see confusing M2 errors.
pytestmark = pytest.mark.skipif(
    not _m1_implemented(),
    reason="M1 (text processing) must be implemented before running M2 tests.",
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_documents():
    """Three tokenized documents for index tests."""
    config = TokenizerConfig()
    pairs = [
        ("fk-001", "Redmi Note 13 5G Mobile Phone 8GB RAM 256GB Storage"),
        ("fk-002", "Samsung Galaxy M14 5G 6GB RAM 128GB Dark Blue"),
        ("fk-003", "Nike Revolution Running Shoes for Men"),
    ]
    return [tokenize_document(doc_id, text, config) for doc_id, text in pairs]


@pytest.fixture
def single_document():
    """One tokenized document."""
    config = TokenizerConfig()
    return [tokenize_document("fk-solo", "Boat Bluetooth Earbuds with Mic", config)]


@pytest.fixture
def duplicate_terms_document():
    """A document where the same term appears multiple times."""
    config = TokenizerConfig()
    return [tokenize_document("fk-dup", "RAM 8GB RAM 16GB RAM 32GB", config)]


# ---------------------------------------------------------------------------
# build_index: structural invariants
# ---------------------------------------------------------------------------

class TestBuildIndex:
    """Invariant tests for build_index."""

    def test_returns_inverted_index(self, sample_documents):
        index = build_index(sample_documents)
        assert isinstance(index, InvertedIndex)

    def test_document_count_matches(self, sample_documents):
        index = build_index(sample_documents)
        assert index.document_count == len(sample_documents)

    def test_total_terms_consistent(self, sample_documents):
        index = build_index(sample_documents)
        expected = sum(doc.token_count for doc in sample_documents)
        assert index.total_terms == expected

    def test_document_lengths_match_token_counts(self, sample_documents):
        index = build_index(sample_documents)
        for doc in sample_documents:
            assert doc.doc_id in index.document_lengths
            assert index.document_lengths[doc.doc_id] == doc.token_count

    def test_average_document_length(self, sample_documents):
        index = build_index(sample_documents)
        expected = index.total_terms / index.document_count
        assert abs(index.average_document_length - expected) < 1e-9

    def test_every_token_has_posting(self, sample_documents):
        """Every token that appears in any document has a key in postings."""
        index = build_index(sample_documents)
        for doc in sample_documents:
            for term in doc.term_counts:
                assert term in index.postings, (
                    f"Term '{term}' from doc '{doc.doc_id}' missing from index"
                )

    def test_one_posting_per_doc_per_term(self, sample_documents):
        """Each posting list has at most one Posting per document."""
        index = build_index(sample_documents)
        for term, posting_list in index.postings.items():
            doc_ids = [p.doc_id for p in posting_list]
            assert len(doc_ids) == len(set(doc_ids)), (
                f"Duplicate doc_ids in posting list for '{term}'"
            )

    def test_term_frequency_matches_source(self, sample_documents):
        """Each posting's term_frequency matches the document's term_counts."""
        index = build_index(sample_documents)
        for doc in sample_documents:
            for term, count in doc.term_counts.items():
                posting_list = index.postings[term]
                matches = [p for p in posting_list if p.doc_id == doc.doc_id]
                assert len(matches) == 1, (
                    f"Expected exactly one posting for '{term}' in '{doc.doc_id}'"
                )
                assert matches[0].term_frequency == count

    def test_no_empty_posting_lists(self, sample_documents):
        """No term maps to an empty list."""
        index = build_index(sample_documents)
        for term, posting_list in index.postings.items():
            assert len(posting_list) > 0, (
                f"Empty posting list for '{term}'"
            )

    def test_no_zero_frequency_postings(self, sample_documents):
        """Every posting has term_frequency > 0."""
        index = build_index(sample_documents)
        for term, posting_list in index.postings.items():
            for posting in posting_list:
                assert posting.term_frequency > 0, (
                    f"Zero frequency for '{term}' in '{posting.doc_id}'"
                )

    def test_posting_doc_ids_are_valid(self, sample_documents):
        """Every doc_id in a posting exists in document_lengths."""
        index = build_index(sample_documents)
        for term, posting_list in index.postings.items():
            for posting in posting_list:
                assert posting.doc_id in index.document_lengths, (
                    f"Unknown doc_id '{posting.doc_id}' in posting for '{term}'"
                )

    def test_posting_lists_sorted_by_doc_id(self, sample_documents):
        """Posting lists are sorted by doc_id for deterministic output."""
        index = build_index(sample_documents)
        for term, posting_list in index.postings.items():
            doc_ids = [p.doc_id for p in posting_list]
            assert doc_ids == sorted(doc_ids), (
                f"Posting list for '{term}' not sorted by doc_id"
            )

    def test_deterministic_output(self, sample_documents):
        """Same input produces identical output every time."""
        index_a = build_index(sample_documents)
        index_b = build_index(sample_documents)
        assert index_a.document_count == index_b.document_count
        assert index_a.total_terms == index_b.total_terms
        assert index_a.document_lengths == index_b.document_lengths
        assert set(index_a.postings.keys()) == set(index_b.postings.keys())
        for term in index_a.postings:
            list_a = index_a.postings[term]
            list_b = index_b.postings[term]
            assert len(list_a) == len(list_b)
            for pa, pb in zip(list_a, list_b):
                assert pa.doc_id == pb.doc_id
                assert pa.term_frequency == pb.term_frequency


class TestBuildIndexEdgeCases:
    """Edge cases and boundary conditions."""

    def test_empty_document_list(self):
        """Building from zero documents produces an empty index."""
        index = build_index([])
        assert index.document_count == 0
        assert index.total_terms == 0
        assert len(index.postings) == 0
        assert len(index.document_lengths) == 0
        assert index.average_document_length == 0.0

    def test_single_document(self, single_document):
        index = build_index(single_document)
        assert index.document_count == 1
        doc = single_document[0]
        assert index.document_lengths[doc.doc_id] == doc.token_count

    def test_repeated_term_frequency(self, duplicate_terms_document):
        """A term appearing multiple times in one doc has correct tf."""
        index = build_index(duplicate_terms_document)
        doc = duplicate_terms_document[0]
        ram_count = doc.term_counts.get("ram", 0)
        if ram_count > 0:
            postings = index.postings.get("ram", [])
            assert len(postings) == 1
            assert postings[0].term_frequency == ram_count


# ---------------------------------------------------------------------------
# lookup
# ---------------------------------------------------------------------------

class TestLookup:
    """Tests for the lookup function."""

    def test_known_term_returns_postings(self, sample_documents):
        index = build_index(sample_documents)
        # "5g" appears in fk-001 and fk-002
        results = lookup(index, "5g")
        assert len(results) > 0
        assert all(isinstance(p, Posting) for p in results)

    def test_unknown_term_returns_empty(self, sample_documents):
        index = build_index(sample_documents)
        results = lookup(index, "nonexistentterm12345")
        assert results == []

    def test_lookup_matches_postings(self, sample_documents):
        """lookup returns the same list as direct postings access."""
        index = build_index(sample_documents)
        for term in index.postings:
            assert lookup(index, term) == index.postings[term]

    def test_single_doc_term(self, sample_documents):
        """A term unique to one document returns exactly one posting."""
        index = build_index(sample_documents)
        # "nike" should only be in fk-003
        results = lookup(index, "nike")
        if results:
            assert len(results) == 1
            assert results[0].doc_id == "fk-003"
