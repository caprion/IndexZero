"""Tests for M4: Evaluation metrics.

Core tests use hand-built fixtures — no M3 dependency required.
The metrics are pure math functions that operate on ranked lists
and relevance judgments. No search pipeline needed.

Test philosophy: exact-value checks on tiny fixtures and
relational/invariant tests (perfect > reversed, threshold effects, etc.).
"""

from __future__ import annotations

import math

import pytest

from indexzero.evaluation import (
    EvalReport,
    QueryMetrics,
    QueryResults,
    RelevanceJudgment,
    evaluate,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


# ---------------------------------------------------------------------------
# Fixtures: hand-built result lists and judgments (no M3 dependency)
# ---------------------------------------------------------------------------


@pytest.fixture
def perfect_results():
    """Results in ideal order: Exact, Substitute, Complement."""
    return QueryResults(query_id="q1", doc_ids=["d1", "d2", "d3"])


@pytest.fixture
def perfect_judgments():
    return [
        RelevanceJudgment("q1", "d1", 3),  # Exact
        RelevanceJudgment("q1", "d2", 2),  # Substitute
        RelevanceJudgment("q1", "d3", 1),  # Complement
    ]


@pytest.fixture
def reversed_results():
    """Results in worst order: Complement, Substitute, Exact."""
    return QueryResults(query_id="q1", doc_ids=["d3", "d2", "d1"])


@pytest.fixture
def all_irrelevant_judgments():
    """Judgments where all docs have grade 0."""
    return [
        RelevanceJudgment("q1", "d1", 0),
        RelevanceJudgment("q1", "d2", 0),
        RelevanceJudgment("q1", "d3", 0),
    ]


# ---------------------------------------------------------------------------
# precision_at_k tests
# ---------------------------------------------------------------------------


class TestPrecisionAtK:

    def test_perfect_precision(self, perfect_results, perfect_judgments):
        """All relevant (grade >= 2) in top k -> high precision."""
        # d1=3 (relevant), d2=2 (relevant), d3=1 (not relevant at threshold=2)
        result = precision_at_k(perfect_results, perfect_judgments, k=3)
        assert result == pytest.approx(2 / 3)

    def test_no_relevant_results(self, perfect_results, all_irrelevant_judgments):
        """All irrelevant -> 0.0."""
        result = precision_at_k(perfect_results, all_irrelevant_judgments, k=3)
        assert result == 0.0

    def test_unjudged_not_relevant(self):
        """Documents not in judgments are treated as grade 0 (not relevant)."""
        results = QueryResults(query_id="q1", doc_ids=["unknown1", "unknown2"])
        judgments = [RelevanceJudgment("q1", "d1", 3)]
        result = precision_at_k(results, judgments, k=2)
        assert result == 0.0

    def test_threshold_changes_precision(self, perfect_results, perfect_judgments):
        """Complement (grade=1) is relevant at threshold=1, not at threshold=2."""
        # At threshold=1: d1(3), d2(2), d3(1) all relevant -> 3/3 = 1.0
        result_low = precision_at_k(perfect_results, perfect_judgments, k=3, relevance_threshold=1)
        assert result_low == pytest.approx(1.0)
        # At threshold=2: d1(3), d2(2) relevant, d3(1) not -> 2/3
        result_high = precision_at_k(perfect_results, perfect_judgments, k=3, relevance_threshold=2)
        assert result_high == pytest.approx(2 / 3)

    def test_partial_precision(self):
        """Mix of relevant and irrelevant in top-k."""
        results = QueryResults(query_id="q1", doc_ids=["d1", "d2", "d3", "d4"])
        judgments = [
            RelevanceJudgment("q1", "d1", 3),
            RelevanceJudgment("q1", "d2", 0),
            RelevanceJudgment("q1", "d3", 2),
            RelevanceJudgment("q1", "d4", 0),
        ]
        result = precision_at_k(results, judgments, k=4)
        assert result == pytest.approx(2 / 4)

    def test_k_larger_than_results(self, perfect_results, perfect_judgments):
        """k=10 but only 3 results -> divides by k, not len(results)."""
        result = precision_at_k(perfect_results, perfect_judgments, k=10)
        # d1(3) and d2(2) are relevant at threshold=2 -> 2/10
        assert result == pytest.approx(2 / 10)


# ---------------------------------------------------------------------------
# recall_at_k tests
# ---------------------------------------------------------------------------


class TestRecallAtK:

    def test_full_recall(self, perfect_results, perfect_judgments):
        """All relevant found in top-k -> 1.0."""
        # d1(3) and d2(2) are relevant at threshold=2; both in top 3
        result = recall_at_k(perfect_results, perfect_judgments, k=3)
        assert result == pytest.approx(1.0)

    def test_partial_recall(self):
        """Found 1 of 2 relevant docs -> 0.5."""
        results = QueryResults(query_id="q1", doc_ids=["d1"])
        judgments = [
            RelevanceJudgment("q1", "d1", 3),
            RelevanceJudgment("q1", "d2", 2),
        ]
        result = recall_at_k(results, judgments, k=1)
        assert result == pytest.approx(0.5)

    def test_no_relevant_returns_one(self, perfect_results, all_irrelevant_judgments):
        """Zero relevant docs in qrels -> 1.0 (vacuously true)."""
        result = recall_at_k(perfect_results, all_irrelevant_judgments, k=3)
        assert result == pytest.approx(1.0)

    def test_recall_vs_precision_different(self):
        """When total relevant > k, recall and precision differ."""
        results = QueryResults(query_id="q1", doc_ids=["d1"])
        judgments = [
            RelevanceJudgment("q1", "d1", 3),
            RelevanceJudgment("q1", "d2", 3),
            RelevanceJudgment("q1", "d3", 2),
        ]
        # P@1 = 1/1 = 1.0
        p = precision_at_k(results, judgments, k=1)
        # R@1 = 1/3 ≈ 0.333
        r = recall_at_k(results, judgments, k=1)
        assert p == pytest.approx(1.0)
        assert r == pytest.approx(1 / 3)
        assert p != r

    def test_zero_recall(self):
        """Relevant docs exist but none found in top-k -> 0.0."""
        results = QueryResults(query_id="q1", doc_ids=["d3", "d4"])
        judgments = [
            RelevanceJudgment("q1", "d1", 3),
            RelevanceJudgment("q1", "d2", 2),
            RelevanceJudgment("q1", "d3", 0),
            RelevanceJudgment("q1", "d4", 0),
        ]
        result = recall_at_k(results, judgments, k=2)
        assert result == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# reciprocal_rank tests
# ---------------------------------------------------------------------------


class TestReciprocalRank:

    def test_first_position(self, perfect_results, perfect_judgments):
        """Relevant at rank 1 -> RR = 1.0."""
        result = reciprocal_rank(perfect_results, perfect_judgments)
        assert result == pytest.approx(1.0)

    def test_third_position(self):
        """First relevant at rank 3 -> RR = 1/3."""
        results = QueryResults(query_id="q1", doc_ids=["d3", "d4", "d1"])
        judgments = [
            RelevanceJudgment("q1", "d1", 3),
            RelevanceJudgment("q1", "d3", 0),
            RelevanceJudgment("q1", "d4", 0),
        ]
        result = reciprocal_rank(results, judgments)
        assert result == pytest.approx(1 / 3)

    def test_no_relevant_returns_zero(self, perfect_results, all_irrelevant_judgments):
        """No relevant results -> 0.0."""
        result = reciprocal_rank(perfect_results, all_irrelevant_judgments)
        assert result == 0.0

    def test_only_first_matters(self):
        """Multiple relevant results — only the first one counts."""
        results = QueryResults(query_id="q1", doc_ids=["d1", "d2", "d3"])
        judgments = [
            RelevanceJudgment("q1", "d1", 3),
            RelevanceJudgment("q1", "d2", 3),
            RelevanceJudgment("q1", "d3", 2),
        ]
        result = reciprocal_rank(results, judgments)
        # First relevant is at rank 1 -> 1.0 regardless of d2 and d3
        assert result == pytest.approx(1.0)

    def test_threshold_changes_rank(self):
        """Different thresholds change which doc is 'first relevant'."""
        results = QueryResults(query_id="q1", doc_ids=["d1", "d2"])
        judgments = [
            RelevanceJudgment("q1", "d1", 1),  # Complement
            RelevanceJudgment("q1", "d2", 3),  # Exact
        ]
        # At threshold=2: d1 is not relevant, d2 is -> RR = 1/2
        rr_high = reciprocal_rank(results, judgments, relevance_threshold=2)
        assert rr_high == pytest.approx(0.5)
        # At threshold=1: d1 is relevant -> RR = 1.0
        rr_low = reciprocal_rank(results, judgments, relevance_threshold=1)
        assert rr_low == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# ndcg_at_k tests
# ---------------------------------------------------------------------------


class TestNdcgAtK:

    def test_perfect_ranking_is_one(self, perfect_results, perfect_judgments):
        """Ideal order -> nDCG = 1.0."""
        result = ndcg_at_k(perfect_results, perfect_judgments, k=3)
        assert result == pytest.approx(1.0)

    def test_reversed_ranking_less_than_one(self, reversed_results, perfect_judgments):
        """Worst order -> nDCG < 1.0."""
        result = ndcg_at_k(reversed_results, perfect_judgments, k=3)
        assert result < 1.0

    def test_position_matters(self):
        """Placing a high-grade doc first scores better than placing it last."""
        judgments = [
            RelevanceJudgment("q1", "d1", 3),
            RelevanceJudgment("q1", "d2", 0),
        ]
        results_good = QueryResults(query_id="q1", doc_ids=["d1", "d2"])
        results_bad = QueryResults(query_id="q1", doc_ids=["d2", "d1"])
        ndcg_good = ndcg_at_k(results_good, judgments, k=2)
        ndcg_bad = ndcg_at_k(results_bad, judgments, k=2)
        assert ndcg_good > ndcg_bad

    def test_ndcg_normalized_range(self, perfect_results, perfect_judgments):
        """nDCG is always in [0.0, 1.0]."""
        result = ndcg_at_k(perfect_results, perfect_judgments, k=3)
        assert 0.0 <= result <= 1.0

    def test_no_relevant_docs_returns_zero(self, perfect_results, all_irrelevant_judgments):
        """All grade 0 -> IDCG = 0 -> nDCG = 0.0."""
        result = ndcg_at_k(perfect_results, all_irrelevant_judgments, k=3)
        assert result == 0.0

    def test_exact_value_known(self):
        """Hand-computed nDCG for a known input.

        results = [d1, d2, d3], grades = [3, 0, 2], k=3
        DCG  = 3/log2(2) + 0/log2(3) + 2/log2(4) = 3/1 + 0 + 2/2 = 4.0
        IDCG = 3/log2(2) + 2/log2(3) + 0/log2(4) = 3 + 1.2618... + 0 = 4.2618...
        nDCG = 4.0 / 4.2618... ≈ 0.9386
        """
        results = QueryResults(query_id="q1", doc_ids=["d1", "d2", "d3"])
        judgments = [
            RelevanceJudgment("q1", "d1", 3),
            RelevanceJudgment("q1", "d2", 0),
            RelevanceJudgment("q1", "d3", 2),
        ]
        dcg = 3 / math.log2(2) + 0 / math.log2(3) + 2 / math.log2(4)
        idcg = 3 / math.log2(2) + 2 / math.log2(3) + 0 / math.log2(4)
        expected = dcg / idcg
        result = ndcg_at_k(results, judgments, k=3)
        assert result == pytest.approx(expected, abs=1e-4)

    def test_single_result(self):
        """k=1 with one relevant doc at rank 1 -> nDCG = 1.0."""
        results = QueryResults(query_id="q1", doc_ids=["d1"])
        judgments = [RelevanceJudgment("q1", "d1", 3)]
        result = ndcg_at_k(results, judgments, k=1)
        assert result == pytest.approx(1.0)

    def test_unjudged_docs_treated_as_zero(self):
        """Documents not in judgments get grade 0 for nDCG calculation."""
        results = QueryResults(query_id="q1", doc_ids=["d1", "d_unjudged", "d2"])
        judgments = [
            RelevanceJudgment("q1", "d1", 3),
            RelevanceJudgment("q1", "d2", 2),
        ]
        # d_unjudged gets grade 0 — nDCG should be less than perfect
        result = ndcg_at_k(results, judgments, k=3)
        assert 0.0 < result < 1.0
        # Compare with result where unjudged doc has explicit grade 0
        explicit_judgments = judgments + [RelevanceJudgment("q1", "d_unjudged", 0)]
        explicit_result = ndcg_at_k(results, explicit_judgments, k=3)
        assert result == pytest.approx(explicit_result)


# ---------------------------------------------------------------------------
# evaluate tests
# ---------------------------------------------------------------------------


class TestEvaluate:

    def test_single_query(self, perfect_results, perfect_judgments):
        """Evaluate with one query matches individual metric calls."""
        report = evaluate([perfect_results], perfect_judgments, k=3)
        assert report.num_queries == 1
        assert report.k == 3

        qm = report.per_query[0]
        assert qm.precision_at_k == pytest.approx(
            precision_at_k(perfect_results, perfect_judgments, k=3)
        )
        assert qm.recall_at_k == pytest.approx(
            recall_at_k(perfect_results, perfect_judgments, k=3)
        )
        assert qm.reciprocal_rank == pytest.approx(
            reciprocal_rank(perfect_results, perfect_judgments)
        )
        assert qm.ndcg_at_k == pytest.approx(
            ndcg_at_k(perfect_results, perfect_judgments, k=3)
        )

    def test_multi_query_averages(self):
        """Two queries, verify means are correct averages."""
        results_q1 = QueryResults(query_id="q1", doc_ids=["d1", "d2"])
        results_q2 = QueryResults(query_id="q2", doc_ids=["d3"])
        judgments = [
            RelevanceJudgment("q1", "d1", 3),
            RelevanceJudgment("q1", "d2", 0),
            RelevanceJudgment("q2", "d3", 2),
        ]
        report = evaluate([results_q1, results_q2], judgments, k=2)
        assert report.num_queries == 2

        # Verify means are averages of per-query values
        p_values = [m.precision_at_k for m in report.per_query]
        assert report.mean_precision_at_k == pytest.approx(sum(p_values) / 2)

        r_values = [m.recall_at_k for m in report.per_query]
        assert report.mean_recall_at_k == pytest.approx(sum(r_values) / 2)

        rr_values = [m.reciprocal_rank for m in report.per_query]
        assert report.mean_reciprocal_rank == pytest.approx(sum(rr_values) / 2)

        ndcg_values = [m.ndcg_at_k for m in report.per_query]
        assert report.mean_ndcg_at_k == pytest.approx(sum(ndcg_values) / 2)

    def test_empty_results(self):
        """No results -> all zeros."""
        report = evaluate([], [], k=10)
        assert report.num_queries == 0
        assert report.mean_precision_at_k == 0.0
        assert report.mean_recall_at_k == 0.0
        assert report.mean_reciprocal_rank == 0.0
        assert report.mean_ndcg_at_k == 0.0

    def test_report_fields(self, perfect_results, perfect_judgments):
        """Verify k and num_queries are set in the report."""
        report = evaluate([perfect_results], perfect_judgments, k=5)
        assert report.k == 5
        assert report.num_queries == 1
        assert len(report.per_query) == 1
        assert isinstance(report, EvalReport)
        assert isinstance(report.per_query[0], QueryMetrics)

    def test_threshold_propagates(self):
        """evaluate() passes relevance_threshold to P@k and R@k."""
        results = QueryResults(query_id="q1", doc_ids=["d1", "d2"])
        judgments = [
            RelevanceJudgment("q1", "d1", 1),  # below default threshold 2
            RelevanceJudgment("q1", "d2", 3),
        ]
        # threshold=2 (default): d1 is irrelevant, d2 is relevant
        report_strict = evaluate([results], judgments, k=2, relevance_threshold=2)
        # threshold=1: both are relevant
        report_lenient = evaluate([results], judgments, k=2, relevance_threshold=1)

        assert report_strict.mean_precision_at_k == pytest.approx(0.5)
        assert report_lenient.mean_precision_at_k == pytest.approx(1.0)

    def test_k_zero_raises(self):
        """k=0 should raise ValueError, not ZeroDivisionError."""
        results = QueryResults(query_id="q1", doc_ids=["d1"])
        judgments = [RelevanceJudgment("q1", "d1", 3)]
        with pytest.raises(ValueError):
            precision_at_k(results, judgments, k=0)
