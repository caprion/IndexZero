from __future__ import annotations

import pytest

from indexzero.query_language import (
    AndNode,
    NearNode,
    NotNode,
    OrNode,
    PhraseNode,
    QueryParseError,
    TermNode,
    parse_query,
)


class TestParseQuery:
    def test_phrase_node(self) -> None:
        node = parse_query('"wireless earbuds"')
        assert node == PhraseNode(("wireless", "earbuds"))

    def test_near_node(self) -> None:
        node = parse_query("wireless NEAR/3 earbuds")
        assert node == NearNode("wireless", "earbuds", 3)

    def test_and_has_higher_precedence_than_or(self) -> None:
        node = parse_query("samsung OR redmi AND phone")
        assert node == OrNode(
            left=TermNode("samsung"),
            right=AndNode(TermNode("redmi"), TermNode("phone")),
        )

    def test_parentheses_override_precedence(self) -> None:
        node = parse_query("(samsung OR redmi) AND phone")
        assert node == AndNode(
            left=OrNode(TermNode("samsung"), TermNode("redmi")),
            right=TermNode("phone"),
        )

    def test_not_binds_tightly(self) -> None:
        node = parse_query("samsung AND NOT case")
        assert node == AndNode(
            left=TermNode("samsung"),
            right=NotNode(TermNode("case")),
        )

    def test_unclosed_quote_raises(self) -> None:
        with pytest.raises(QueryParseError):
            parse_query('"wireless earbuds')
