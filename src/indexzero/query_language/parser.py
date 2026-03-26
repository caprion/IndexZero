"""Parser for the M5 structured query language."""

from __future__ import annotations

import re
from dataclasses import dataclass

from ..text_processing import TokenizerConfig, tokenize_text
from .contracts import (
    AndNode,
    NearNode,
    NotNode,
    OrNode,
    PhraseNode,
    QueryNode,
    QueryParseError,
    TermNode,
)


TOKEN_PATTERN = re.compile(
    r'"[^"]*"|\(|\)|\bNEAR/\d+\b|\bAND\b|\bOR\b|\bNOT\b|[^\s()]+',
)


@dataclass(frozen=True)
class _Token:
    kind: str
    value: str


def _normalize_single_term(term_text: str, config: TokenizerConfig) -> str:
    tokens = tokenize_text(term_text, config)
    if len(tokens) != 1:
        raise QueryParseError(f"Expected exactly one term, got {term_text!r}")
    return tokens[0]


def _tokenize_query(query_text: str) -> list[_Token]:
    tokens: list[_Token] = []
    for raw in TOKEN_PATTERN.findall(query_text):
        if raw == "(":
            tokens.append(_Token("LPAREN", raw))
        elif raw == ")":
            tokens.append(_Token("RPAREN", raw))
        elif raw in {"AND", "OR", "NOT"}:
            tokens.append(_Token(raw, raw))
        elif raw.startswith("NEAR/"):
            tokens.append(_Token("NEAR", raw))
        elif raw.startswith('"'):
            if not raw.endswith('"') or len(raw) < 2:
                raise QueryParseError("Unclosed quote in phrase query")
            tokens.append(_Token("PHRASE", raw[1:-1]))
        else:
            tokens.append(_Token("TERM", raw))
    return tokens


class _Parser:
    def __init__(self, tokens: list[_Token], config: TokenizerConfig) -> None:
        self._tokens = tokens
        self._config = config
        self._index = 0

    def parse(self) -> QueryNode:
        if not self._tokens:
            raise QueryParseError("Query is empty")
        node = self._parse_or()
        if self._peek() is not None:
            raise QueryParseError(f"Unexpected token {self._peek().value!r}")
        return node

    def _parse_or(self) -> QueryNode:
        node = self._parse_and()
        while self._match("OR"):
            node = OrNode(left=node, right=self._parse_and())
        return node

    def _parse_and(self) -> QueryNode:
        node = self._parse_unary()
        while True:
            if self._match("AND"):
                node = AndNode(left=node, right=self._parse_unary())
            elif self._can_start_expression(self._peek()):
                node = AndNode(left=node, right=self._parse_unary())
            else:
                return node

    def _parse_unary(self) -> QueryNode:
        if self._match("NOT"):
            return NotNode(child=self._parse_unary())
        return self._parse_primary()

    def _parse_primary(self) -> QueryNode:
        token = self._peek()
        if token is None:
            raise QueryParseError("Unexpected end of query")

        if self._match("LPAREN"):
            node = self._parse_or()
            self._expect("RPAREN")
            return node

        if token.kind == "PHRASE":
            self._advance()
            phrase_terms = tuple(tokenize_text(token.value, self._config))
            if not phrase_terms:
                raise QueryParseError("Phrase query did not contain any terms")
            return PhraseNode(terms=phrase_terms)

        if token.kind == "TERM":
            self._advance()
            left_term = _normalize_single_term(token.value, self._config)
            if self._peek() and self._peek().kind == "NEAR":
                near_token = self._advance()
                right_token = self._expect("TERM")
                right_term = _normalize_single_term(right_token.value, self._config)
                distance = int(near_token.value.split("/", maxsplit=1)[1])
                if distance < 1:
                    raise QueryParseError("NEAR distance must be >= 1")
                return NearNode(
                    left_term=left_term,
                    right_term=right_term,
                    distance=distance,
                )
            return TermNode(term=left_term)

        raise QueryParseError(f"Unexpected token {token.value!r}")

    def _peek(self) -> _Token | None:
        if self._index >= len(self._tokens):
            return None
        return self._tokens[self._index]

    def _advance(self) -> _Token:
        token = self._tokens[self._index]
        self._index += 1
        return token

    def _match(self, kind: str) -> bool:
        token = self._peek()
        if token is not None and token.kind == kind:
            self._index += 1
            return True
        return False

    def _expect(self, kind: str) -> _Token:
        token = self._peek()
        if token is None or token.kind != kind:
            raise QueryParseError(
                f"Expected {kind}, got {token.value!r}" if token else f"Expected {kind}"
            )
        self._index += 1
        return token

    @staticmethod
    def _can_start_expression(token: _Token | None) -> bool:
        return token is not None and token.kind in {"TERM", "PHRASE", "LPAREN", "NOT"}


def parse_query(
    query_text: str,
    config: TokenizerConfig | None = None,
) -> QueryNode:
    config = config or TokenizerConfig()
    tokens = _tokenize_query(query_text)
    parser = _Parser(tokens, config)
    return parser.parse()
