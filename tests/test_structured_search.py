from __future__ import annotations

import pytest

from indexzero.query_language import QueryParseError
from indexzero.query_processing import build_positional_index, search_structured
from indexzero.scoring import ScorerConfig
from indexzero.indexing import build_index
from indexzero.text_processing import TokenizerConfig, tokenize_document


@pytest.fixture
def structured_indexes():
    config = TokenizerConfig()
    documents = [
        tokenize_document("d1", "Wireless earbuds with charging case", config),
        tokenize_document("d2", "Wireless bluetooth headphones for travel", config),
        tokenize_document("d3", "Earbuds for running with wireless connectivity", config),
        tokenize_document("d4", "Samsung phone case for galaxy", config),
        tokenize_document("d5", "Samsung galaxy phone", config),
    ]
    return (
        build_index(documents),
        build_positional_index(documents),
        ScorerConfig(),
        config,
    )


def test_phrase_query_is_stricter_than_bag_of_words(structured_indexes) -> None:
    index, positional_index, scorer_config, config = structured_indexes

    plain_results = search_structured(
        "wireless earbuds",
        index,
        positional_index,
        scorer_config,
        tokenizer_config=config,
    )
    phrase_results = search_structured(
        '"wireless earbuds"',
        index,
        positional_index,
        scorer_config,
        tokenizer_config=config,
    )

    assert [result.doc_id for result in plain_results[:3]] == ["d1", "d3", "d2"]
    assert [result.doc_id for result in phrase_results] == ["d1"]


def test_boolean_and_not_filters_candidates(structured_indexes) -> None:
    index, positional_index, scorer_config, config = structured_indexes

    results = search_structured(
        "samsung AND phone NOT case",
        index,
        positional_index,
        scorer_config,
        tokenizer_config=config,
    )

    assert [result.doc_id for result in results] == ["d5"]


def test_near_query_matches_within_window(structured_indexes) -> None:
    index, positional_index, scorer_config, config = structured_indexes

    results = search_structured(
        "wireless NEAR/2 earbuds",
        index,
        positional_index,
        scorer_config,
        tokenizer_config=config,
    )

    assert [result.doc_id for result in results] == ["d1"]


def test_all_negative_query_is_rejected(structured_indexes) -> None:
    index, positional_index, scorer_config, config = structured_indexes

    with pytest.raises(QueryParseError):
        search_structured(
            "NOT case",
            index,
            positional_index,
            scorer_config,
            tokenizer_config=config,
        )
