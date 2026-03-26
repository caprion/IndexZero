"""Execution utilities for M5 structured lexical search."""

from __future__ import annotations

import re

from ..indexing import InvertedIndex
from ..query_language import (
    AndNode,
    NearNode,
    NotNode,
    OrNode,
    PhraseNode,
    QueryNode,
    QueryParseError,
    TermNode,
    parse_query,
)
from ..scoring import ScorerConfig, SearchResult, search
from ..text_processing import TokenizerConfig, tokenize_text
from .contracts import PositionalIndex


STRUCTURED_OPERATOR_PATTERN = re.compile(r"\b(?:AND|OR|NOT|NEAR/\d+)\b")


def _all_doc_ids(index: InvertedIndex) -> set[str]:
    return set(index.document_lengths)


def _doc_ids_for_term(term: str, index: InvertedIndex) -> set[str]:
    return {posting.doc_id for posting in index.postings.get(term, [])}


def _positions_for_term(term: str, positional_index: PositionalIndex, doc_id: str) -> list[int]:
    for posting in positional_index.postings.get(term, []):
        if posting.doc_id == doc_id:
            return posting.positions
    return []


def match_phrase(phrase_terms: tuple[str, ...], positional_index: PositionalIndex) -> set[str]:
    if not phrase_terms:
        return set()

    candidate_docs = {
        posting.doc_id for posting in positional_index.postings.get(phrase_terms[0], [])
    }
    for term in phrase_terms[1:]:
        candidate_docs &= {
            posting.doc_id for posting in positional_index.postings.get(term, [])
        }

    matches: set[str] = set()
    for doc_id in candidate_docs:
        first_positions = _positions_for_term(phrase_terms[0], positional_index, doc_id)
        other_positions = [
            set(_positions_for_term(term, positional_index, doc_id))
            for term in phrase_terms[1:]
        ]
        for start in first_positions:
            if all((start + offset) in positions for offset, positions in enumerate(other_positions, start=1)):
                matches.add(doc_id)
                break
    return matches


def match_near(left_term: str, right_term: str, distance: int, positional_index: PositionalIndex) -> set[str]:
    left_docs = {posting.doc_id for posting in positional_index.postings.get(left_term, [])}
    right_docs = {posting.doc_id for posting in positional_index.postings.get(right_term, [])}
    matches: set[str] = set()

    for doc_id in left_docs & right_docs:
        left_positions = _positions_for_term(left_term, positional_index, doc_id)
        right_positions = _positions_for_term(right_term, positional_index, doc_id)
        left_index = 0
        right_index = 0
        while left_index < len(left_positions) and right_index < len(right_positions):
            gap = abs(left_positions[left_index] - right_positions[right_index])
            if gap <= distance:
                matches.add(doc_id)
                break
            if left_positions[left_index] < right_positions[right_index]:
                left_index += 1
            else:
                right_index += 1
    return matches


def retrieve(query_ast: QueryNode, index: InvertedIndex, positional_index: PositionalIndex) -> set[str]:
    if isinstance(query_ast, TermNode):
        return _doc_ids_for_term(query_ast.term, index)
    if isinstance(query_ast, PhraseNode):
        return match_phrase(query_ast.terms, positional_index)
    if isinstance(query_ast, NearNode):
        return match_near(
            query_ast.left_term,
            query_ast.right_term,
            query_ast.distance,
            positional_index,
        )
    if isinstance(query_ast, AndNode):
        return retrieve(query_ast.left, index, positional_index) & retrieve(
            query_ast.right,
            index,
            positional_index,
        )
    if isinstance(query_ast, OrNode):
        return retrieve(query_ast.left, index, positional_index) | retrieve(
            query_ast.right,
            index,
            positional_index,
        )
    if isinstance(query_ast, NotNode):
        return _all_doc_ids(index) - retrieve(query_ast.child, index, positional_index)
    raise TypeError(f"Unsupported query node: {type(query_ast)!r}")


def extract_query_terms(query_ast: QueryNode) -> list[str]:
    if isinstance(query_ast, TermNode):
        return [query_ast.term]
    if isinstance(query_ast, PhraseNode):
        return list(query_ast.terms)
    if isinstance(query_ast, NearNode):
        return [query_ast.left_term, query_ast.right_term]
    if isinstance(query_ast, (AndNode, OrNode)):
        return extract_query_terms(query_ast.left) + extract_query_terms(query_ast.right)
    if isinstance(query_ast, NotNode):
        return extract_query_terms(query_ast.child)
    raise TypeError(f"Unsupported query node: {type(query_ast)!r}")


def search_structured(
    query_text: str,
    index: InvertedIndex,
    positional_index: PositionalIndex,
    scorer_config: ScorerConfig,
    top_k: int = 10,
    tokenizer_config: TokenizerConfig | None = None,
) -> list[SearchResult]:
    tokenizer_config = tokenizer_config or TokenizerConfig()
    if not query_text.strip():
        return []

    has_structure = (
        '"' in query_text
        or "(" in query_text
        or ")" in query_text
        or STRUCTURED_OPERATOR_PATTERN.search(query_text) is not None
    )
    if not has_structure:
        query_terms = tokenize_text(query_text, tokenizer_config)
        return search(query_terms, index, scorer_config, top_k=top_k)

    query_ast = parse_query(query_text, tokenizer_config)
    if isinstance(query_ast, NotNode):
        raise QueryParseError("All-negative queries are not supported")

    matched_doc_ids = retrieve(query_ast, index, positional_index)
    if not matched_doc_ids:
        return []

    query_terms = extract_query_terms(query_ast)
    ranked = search(
        query_terms,
        index,
        scorer_config,
        top_k=max(top_k, index.document_count),
    )
    filtered = [result for result in ranked if result.doc_id in matched_doc_ids]
    return filtered[:top_k]
