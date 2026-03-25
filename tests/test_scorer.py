"""Tests for M3: BM25 scoring and search.

Core tests use hand-built InvertedIndex fixtures — no M2 dependency.
Integration tests that need build_index use a skip guard.

Test philosophy: mix of exact-value checks on tiny fixtures and
relational/invariant tests (rare > common, shorter > longer, etc.).
"""

from __future__ import annotations

import math

import pytest

from indexzero.indexing.contracts import InvertedIndex, Posting
from indexzero.scoring import ScorerConfig, SearchResult, compute_idf, score_bm25, search


# ---------------------------------------------------------------------------
# Fixtures: hand-built indexes (no M2 dependency)
# ---------------------------------------------------------------------------

@pytest.fixture
def small_index() -> InvertedIndex:
    """4-doc index designed to show all three IDF regimes.

    d1: "samsung phone"                      (2 tokens)
    d2: "phone case leather"                 (3 tokens)
    d3: "case for phone"                     (3 tokens)
    d4: "for for for phone"                  (4 tokens)

    'samsung' is in 1 doc (rare, positive IDF).
    'phone' is in all 4 docs (common, negative IDF).
    'case' is in 2 docs (IDF = 0 boundary).
    'for' is in 2 docs (IDF = 0 boundary).
    'leather' is in 1 doc (rare, positive IDF).
    """
    return InvertedIndex(
        postings={
            "samsung": [Posting("d1", 1)],
            "phone": [Posting("d1", 1), Posting("d2", 1), Posting("d3", 1), Posting("d4", 1)],
            "case": [Posting("d2", 1), Posting("d3", 1)],
            "leather": [Posting("d2", 1)],
            "for": [Posting("d3", 1), Posting("d4", 3)],
        },
        document_lengths={"d1": 2, "d2": 3, "d3": 3, "d4": 4},
        document_count=4,
        total_terms=12,
    )


@pytest.fixture
def negative_idf_index() -> InvertedIndex:
    """Index where 'the' appears in all docs (df > N/2 -> negative IDF)."""
    return InvertedIndex(
        postings={
            "the": [Posting("d1", 1), Posting("d2", 2), Posting("d3", 1)],
            "rare": [Posting("d1", 1)],
        },
        document_lengths={"d1": 3, "d2": 4, "d3": 2},
        document_count=3,
        total_terms=9,
    )


@pytest.fixture
def default_config() -> ScorerConfig:
    return ScorerConfig()


# ---------------------------------------------------------------------------
# compute_idf tests
# ---------------------------------------------------------------------------

class TestComputeIdf:

    def test_unknown_term_returns_zero(self, small_index):
        assert compute_idf("nonexistent", small_index) == 0.0

    def test_rare_term_higher_than_common(self, small_index):
        """A term in fewer docs should have higher IDF."""
        idf_samsung = compute_idf("samsung", small_index)  # df=2
        idf_phone = compute_idf("phone", small_index)       # df=4
        assert idf_samsung > idf_phone

    def test_negative_idf_for_very_common_term(self, negative_idf_index):
        """Term in all 3 of 3 docs -> df > N/2 -> negative IDF."""
        idf_the = compute_idf("the", negative_idf_index)
        assert idf_the < 0.0

    def test_exact_value_known_fixture(self, small_index):
        """Verify exact IDF computation: samsung df=1, N=4 -> ln((4-1+0.5)/(1+0.5))."""
        expected = math.log((4 - 1 + 0.5) / (1 + 0.5))
        assert compute_idf("samsung", small_index) == pytest.approx(expected)

    def test_same_df_gives_same_idf(self, small_index):
        """case and for both have df=2, so same IDF."""
        assert compute_idf("case", small_index) == pytest.approx(
            compute_idf("for", small_index)
        )

    def test_idf_zero_at_boundary(self, small_index):
        """df = N/2 gives IDF = 0. The term is neither informative nor anti-informative.
        In small_index: df=2, N=4 -> ln((4-2+0.5)/(2+0.5)) = ln(1.0) = 0.0."""
        assert compute_idf("case", small_index) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# score_bm25 tests
# ---------------------------------------------------------------------------

class TestScoreBm25:

    def test_unknown_term_returns_zero(self, small_index, default_config):
        assert score_bm25("nonexistent", "d1", small_index, default_config) == 0.0

    def test_doc_not_in_posting_list_returns_zero(self, small_index, default_config):
        """d3 does not contain 'samsung'."""
        assert score_bm25("samsung", "d3", small_index, default_config) == 0.0

    def test_shorter_doc_scores_higher_same_tf(self, default_config):
        """Same tf, positive IDF, shorter doc should score higher (b > 0)."""
        index = InvertedIndex(
            postings={"rare": [Posting("short", 1), Posting("long", 1)]},
            document_lengths={"short": 3, "long": 10},
            document_count=10,
            total_terms=65,
        )
        score_short = score_bm25("rare", "short", index, default_config)
        score_long = score_bm25("rare", "long", index, default_config)
        assert score_short > score_long

    def test_higher_tf_increases_score(self, default_config):
        """Higher tf should increase score when IDF is positive."""
        index = InvertedIndex(
            postings={"term": [Posting("d1", 1), Posting("d2", 3)]},
            document_lengths={"d1": 5, "d2": 5},
            document_count=10,
            total_terms=50,
        )
        score_tf1 = score_bm25("term", "d1", index, default_config)
        score_tf3 = score_bm25("term", "d2", index, default_config)
        assert score_tf3 > score_tf1

    def test_tf_saturation(self):
        """Doubling tf should less than double the score (diminishing returns).
        Test with b=0 to isolate saturation from length normalization."""
        config_no_length = ScorerConfig(k1=1.2, b=0.0)

        # df=3 in N=20 gives positive IDF
        index = InvertedIndex(
            postings={
                "term": [Posting("d1", 1), Posting("d2", 2), Posting("d3", 4)],
            },
            document_lengths={"d1": 5, "d2": 5, "d3": 5},
            document_count=20,
            total_terms=100,
        )
        s1 = score_bm25("term", "d1", index, config_no_length)
        s2 = score_bm25("term", "d2", index, config_no_length)
        s4 = score_bm25("term", "d3", index, config_no_length)

        # Score increases but at diminishing rate
        assert s2 > s1
        assert s4 > s2
        gain_1_to_2 = s2 - s1
        gain_2_to_4 = s4 - s2
        assert gain_1_to_2 > gain_2_to_4  # diminishing returns

    def test_b_zero_removes_length_normalization(self):
        """With b=0, document length should not affect score."""
        config = ScorerConfig(k1=1.2, b=0.0)
        index = InvertedIndex(
            postings={"term": [Posting("short", 1), Posting("long", 1)]},
            document_lengths={"short": 2, "long": 20},
            document_count=2,
            total_terms=22,
        )
        score_short = score_bm25("term", "short", index, config)
        score_long = score_bm25("term", "long", index, config)
        assert score_short == pytest.approx(score_long)

    def test_exact_value_known_fixture(self, small_index, default_config):
        """Verify exact BM25 for 'samsung' in d1 using the small_index fixture.
        samsung: df=1, N=4 -> IDF = ln(3.5/1.5) = ln(2.333...)
        tf=1, dl=2, avgdl=3.0, k1=1.2, b=0.75"""
        idf = math.log((4 - 1 + 0.5) / (1 + 0.5))  # ln(2.333...) ≈ 0.847
        # denominator = 1 + 1.2 * (1 - 0.75 + 0.75 * 2/3.0) = 1 + 1.2 * 0.75 = 1.9
        dl_norm = 1 - 0.75 + 0.75 * 2 / 3.0
        expected = idf * (1 * 2.2) / (1 + 1.2 * dl_norm)
        assert score_bm25("samsung", "d1", small_index, default_config) == pytest.approx(expected)

    def test_exact_value_rare_term(self):
        """Test exact BM25 value for a rare term where IDF is clearly positive."""
        index = InvertedIndex(
            postings={"rare": [Posting("d1", 2)]},
            document_lengths={"d1": 10},
            document_count=10,
            total_terms=100,
        )
        config = ScorerConfig(k1=1.2, b=0.75)

        # IDF = ln((10 - 1 + 0.5) / (1 + 0.5)) = ln(9.5 / 1.5) = ln(6.333...)
        idf = math.log(9.5 / 1.5)
        # tf=2, dl=10, avgdl=10.0, k1=1.2, b=0.75
        # denominator = 2 + 1.2 * (1 - 0.75 + 0.75 * 10/10) = 2 + 1.2 * 1.0 = 3.2
        # numerator = 2 * (1.2 + 1) = 4.4
        expected = idf * 4.4 / 3.2

        result = score_bm25("rare", "d1", index, config)
        assert result == pytest.approx(expected)


# ---------------------------------------------------------------------------
# search tests
# ---------------------------------------------------------------------------

class TestSearch:

    def test_empty_query_returns_empty(self, small_index, default_config):
        assert search([], small_index, default_config) == []

    def test_unknown_term_returns_empty(self, small_index, default_config):
        assert search(["nonexistent"], small_index, default_config) == []

    def test_single_term_query(self, small_index, default_config):
        results = search(["samsung"], small_index, default_config)
        assert len(results) == 1
        assert all(isinstance(r, SearchResult) for r in results)
        assert results[0].doc_id == "d1"

    def test_multi_term_scores_are_additive(self, small_index, default_config):
        """Score for ["samsung", "phone"] should equal
        score_bm25("samsung", doc) + score_bm25("phone", doc) for each doc."""
        results = search(["samsung", "phone"], small_index, default_config)
        for result in results:
            expected = (
                score_bm25("samsung", result.doc_id, small_index, default_config)
                + score_bm25("phone", result.doc_id, small_index, default_config)
            )
            assert result.score == pytest.approx(expected)

    def test_unknown_query_term_contributes_zero(self, small_index, default_config):
        """Adding an unknown term should not change scores."""
        results_without = search(["samsung"], small_index, default_config)
        results_with = search(["samsung", "nonexistent"], small_index, default_config)
        assert len(results_without) == len(results_with)
        for r1, r2 in zip(results_without, results_with):
            assert r1.doc_id == r2.doc_id
            assert r1.score == pytest.approx(r2.score)

    def test_sorted_by_score_descending(self, small_index, default_config):
        results = search(["samsung", "phone"], small_index, default_config)
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_tiebreak_by_doc_id_ascending(self):
        """When scores are equal, doc_id should be sorted ascending."""
        index = InvertedIndex(
            postings={"term": [Posting("b-doc", 1), Posting("a-doc", 1)]},
            document_lengths={"a-doc": 5, "b-doc": 5},
            document_count=2,
            total_terms=10,
        )
        config = ScorerConfig()
        results = search(["term"], index, config)
        assert results[0].doc_id == "a-doc"
        assert results[1].doc_id == "b-doc"

    def test_top_k_truncation(self, small_index, default_config):
        results = search(["phone"], small_index, default_config, top_k=2)
        assert len(results) <= 2

    def test_top_k_larger_than_results(self, small_index, default_config):
        results = search(["samsung"], small_index, default_config, top_k=100)
        assert len(results) == 1  # only d1 contains samsung

    def test_duplicate_query_terms_count_twice(self, small_index, default_config):
        """Docstring says duplicate terms score per occurrence."""
        single = search(["samsung"], small_index, default_config)
        double = search(["samsung", "samsung"], small_index, default_config)
        assert len(single) == len(double)
        for s, d in zip(single, double):
            assert d.score == pytest.approx(s.score * 2)

    def test_empty_index(self, default_config):
        empty = InvertedIndex()
        assert search(["anything"], empty, default_config) == []


# ---------------------------------------------------------------------------
# Integration tests (require M2 build_index to work)
# ---------------------------------------------------------------------------

def _m2_core_implemented() -> bool:
    """Check if M2 build_index + lookup actually work."""
    try:
        from indexzero.indexing import build_index, lookup
        from indexzero.text_processing import TokenizerConfig, tokenize_document

        doc = tokenize_document("test-1", "hello world hello", TokenizerConfig())
        index = build_index([doc])
        return (
            index.document_count == 1
            and index.document_lengths.get("test-1") == doc.token_count
            and len(index.postings.get("hello", [])) == 1
            and index.postings["hello"][0].term_frequency == 2
            and lookup(index, "hello")[0].doc_id == "test-1"
        )
    except Exception:
        return False


@pytest.mark.skipif(not _m2_core_implemented(), reason="M2 not yet implemented")
class TestSearchIntegration:
    """End-to-end tests using real M1 tokenizer + M2 build_index."""

    def test_search_on_real_pipeline(self):
        from indexzero.indexing import build_index
        from indexzero.text_processing import TokenizerConfig, tokenize_document

        config = TokenizerConfig()
        docs = [
            tokenize_document("fk-001", "Samsung Galaxy M14 5G 128GB Blue", config),
            tokenize_document("fk-002", "Nike Running Shoes for Men", config),
            tokenize_document("fk-003", "Boat Bluetooth Earbuds with Mic", config),
            tokenize_document("fk-004", "Samsung Galaxy Tab S6 Lite WiFi", config),
        ]
        index = build_index(docs)
        scorer_config = ScorerConfig()

        results = search(["samsung"], index, scorer_config)
        doc_ids = {r.doc_id for r in results}
        assert doc_ids == {"fk-001", "fk-004"}

    def test_multi_term_search_real_pipeline(self):
        from indexzero.indexing import build_index
        from indexzero.text_processing import TokenizerConfig, tokenize_document

        config = TokenizerConfig()
        docs = [
            tokenize_document("fk-001", "Samsung Galaxy M14 5G 128GB Blue", config),
            tokenize_document("fk-002", "Nike Running Shoes for Men", config),
            tokenize_document("fk-003", "Samsung Galaxy Watch Active", config),
        ]
        index = build_index(docs)
        scorer_config = ScorerConfig()

        # "samsung galaxy" should rank fk-001 and fk-003 above fk-002
        results = search(["samsung", "galaxy"], index, scorer_config)
        assert len(results) == 2
        assert all(r.doc_id in ("fk-001", "fk-003") for r in results)
