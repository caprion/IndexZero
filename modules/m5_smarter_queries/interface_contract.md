# M5 Interface Contract

M5 extends the search system from bag-of-words lexical retrieval to **structured lexical retrieval**.

The contract for this module is intentionally narrow:

- parse query structure
- retrieve or filter lexical candidates
- rank the surviving documents with BM25

This module must not absorb semantic retrieval. That belongs to M6.

## Compatibility goal

M5 must preserve the value of earlier modules:

- M2's `InvertedIndex` remains valid
- M3's `search()` and BM25 scorer remain valid
- M4's evaluation still works on ranked `doc_id` lists

M5 adds new components beside those modules. It does not invalidate them.

## High-level pipeline contract

The structured-search pipeline should look like this:

```text
query_text
  -> parse_query(query_text)
  -> execute_query(query_ast, index, positional_index)
  -> rank_matched_docs(query_terms, matched_doc_ids, index, scorer_config)
  -> list[SearchResult]
```

Each stage should be separable and testable on its own.

## Query parsing contract

`parse_query(query_text) -> QueryNode`

Parses user query text into a structured representation.

### Required behavior

- supports term nodes
- supports phrase nodes
- supports boolean operators: `AND`, `OR`, `NOT`
- supports parentheses
- supports proximity operator: `NEAR/n`
- produces deterministic output for the same input

### Recommended precedence

1. `NOT`
2. `AND`
3. `OR`

Parentheses override precedence.

### Failure behavior

Malformed queries should raise a clear parsing error rather than silently guessing.

Examples of malformed queries:

- unclosed quote
- `AND` with a missing right operand
- malformed `NEAR/n` syntax

## Query AST contract

The query parser should produce a tree of query nodes. The exact class names may vary, but the shape should support these concepts:

| Node kind | Meaning |
|---|---|
| `TermNode` | One normalized term |
| `PhraseNode` | Ordered adjacent sequence of terms |
| `NearNode` | Two terms or subexpressions with a proximity constraint |
| `AndNode` | Both sides must match |
| `OrNode` | Either side may match |
| `NotNode` | Negation of one child |

### AST invariants

- every term stored in the AST should already be normalized consistently with the tokenizer
- phrase nodes preserve term order
- proximity nodes preserve their configured distance
- identical input text produces structurally identical trees

## Positional index contract

M5 requires token positions for phrase and proximity matching.

Add a new positional structure rather than mutating the M2 contract beyond recognition.

Recommended public type:

- `PositionalIndex`

Recommended posting type:

- `PositionalPosting`

### PositionalPosting fields

| Field | Type | Required | Meaning |
|---|---|---|---|
| `doc_id` | `str` | yes | Document identifier |
| `term_frequency` | `int` | yes | Number of occurrences in this doc |
| `positions` | `list[int]` | yes | Sorted token offsets for the term in this doc |

### PositionalIndex fields

| Field | Type | Required | Meaning |
|---|---|---|---|
| `postings` | `dict[str, list[PositionalPosting]]` | yes | Term to positional posting list |
| `document_lengths` | `dict[str, int]` | yes | Reused for ranking/filtering context |
| `document_count` | `int` | yes | Number of indexed documents |
| `total_terms` | `int` | yes | Sum of all token counts |

### Positional invariants

1. `positions` are sorted ascending within each posting
2. `len(positions) == term_frequency`
3. each posting list has at most one posting per `(term, doc_id)`
4. posting lists are sorted by `doc_id`
5. every position is within `[0, document_length - 1]`

## Positional index builder contract

`build_positional_index(documents) -> PositionalIndex`

Consumes the same `TokenizedDocument` output from M1 that M2 consumes.

### Required behavior

- preserves token order as positions
- records all term occurrences
- handles repeated terms in one document correctly
- is deterministic
- returns an empty positional index for empty input

### Relationship to M2

The positional index is an extension for M5. It should not remove the need for M2's simpler inverted index in earlier modules.

Students should be able to explain:

- what the M2 index stores
- what the M5 positional index adds
- why the added information is necessary

## Boolean execution contract

`execute_boolean(query_ast, index) -> set[str]`

Evaluates boolean structure over lexical posting lists.

### Semantics

- `AND` -> intersection
- `OR` -> union
- `NOT` -> subtraction from a positive candidate universe

### Required behavior

- deterministic matched `doc_id` set
- no duplicate `doc_id`s
- correct precedence and parentheses handling

### Scope constraint

Boolean execution is for candidate generation/filtering. It is not a final ranking stage.

## Phrase execution contract

`match_phrase(phrase_terms, positional_index) -> set[str]`

Returns documents containing the exact ordered adjacent sequence.

### Required behavior

A document matches only if:

- it contains all phrase terms
- the terms occur in the same order
- the matched positions are contiguous

### Non-goal

Phrase execution in M5 does not need slop, fuzzy phrases, or field constraints.

## Proximity execution contract

`match_near(left_terms, right_terms, distance, positional_index) -> set[str]`

Returns documents satisfying a proximity rule.

### Required behavior

- documents must contain the relevant terms
- positions must satisfy the documented window rule
- behavior must be deterministic

### Documentation requirement

The implementation must state clearly whether `NEAR/n` is:

- ordered, or
- unordered

Either is acceptable for M5 if the tests and README are consistent.

## Structured retrieval contract

`retrieve(query_ast, index, positional_index) -> set[str]`

Evaluates the full query tree and returns the matched documents.

### Expected role

This function defines **which docs are allowed to compete** in ranking.

It does not decide the final order.

### Required behavior

- term nodes use lexical postings
- phrase nodes use positional matching
- proximity nodes use positional matching
- boolean composition combines child result sets correctly

## Ranking contract

`search_structured(query_text, index, positional_index, scorer_config, top_k) -> list[SearchResult]`

Runs the end-to-end structured lexical search flow.

### Required behavior

1. parse query text
2. compute matched candidate docs
3. rank matched docs using BM25
4. return results sorted by:
   - score descending
   - `doc_id` ascending for ties

### Important constraint

M5 should reuse BM25 for final ranking. It should not introduce a new learned or semantic scorer.

## Query-term extraction contract

Structured ranking still needs lexical terms for BM25.

So M5 should provide a way to extract the normalized lexical terms from the parsed query tree.

Examples:

- `samsung AND phone` -> `["samsung", "phone"]`
- `"wireless earbuds"` -> `["wireless", "earbuds"]`
- `wireless NEAR/3 earbuds` -> `["wireless", "earbuds"]`

Duplicate terms may remain duplicated if you want BM25 query repetition to matter, but that rule should be documented.

## Edge-case contract

The module should define behavior for these cases:

- empty query string
- unknown terms
- all-negative query
- empty index
- empty positional index
- malformed syntax

Recommended defaults:

- empty query -> empty result list
- unknown terms -> empty match set for that clause
- malformed syntax -> explicit parse error
- empty index -> empty result list
- all-negative query -> reject or require one positive root clause

## M4 compatibility contract

M5 still produces ranked document IDs, so M4-style evaluation remains possible.

That means:

- final outputs should be stable `doc_id`s
- result ordering must be deterministic
- `top_k` must still be respected

This is important because M5 should be measurable with the same evaluation mindset built in M4.

## M6 handoff contract

M5 should leave clear room for semantic retrieval.

A good M5 implementation makes these boundaries obvious:

- query parsing is separate from retrieval
- lexical candidate generation is separate from ranking
- ranking is pluggable
- retrieval paths can multiply later

That allows M6 to add:

- vector candidate generation
- semantic similarity scoring

without rewriting the M5 parser or collapsing the ranking pipeline.

## Summary

M5's contract is simple:

1. understand query structure
2. use lexical and positional indexes to find valid candidates
3. rank those candidates with BM25

Nothing more.

If the module starts promising semantics, expansion, or advanced query rewriting, it has crossed into M6+ territory and lost the course progression.
