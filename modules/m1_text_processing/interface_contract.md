# M1 → M2 Interface Contract

M2 (Inverted Index) consumes the output of M1 directly. This contract defines what M2 can rely on.

## TokenizedDocument contract

Each document produced by `tokenize_document()` exposes:

| Field | Type | Required | Meaning |
|---|---|---|---|
| `doc_id` | `str` | yes | Stable identifier for the document |
| `normalized_text` | `str` | yes | Text after all normalization choices |
| `tokens` | `list[str]` | yes | Ordered token sequence |
| `term_counts` | `Counter[str]` | yes | Count of each token in this document |
| `token_count` | `int` (property) | yes | Total number of emitted tokens |

## Vocabulary contract

The vocabulary built by `build_vocabulary()` exposes:

| Field | Type | Required | Meaning |
|---|---|---|---|
| `token_to_id` | `dict[str, int]` | yes | Stable token → integer ID mapping |
| `document_frequency` | `dict[str, int]` | yes | Number of documents containing each token |
| `collection_frequency` | `dict[str, int]` | yes | Total corpus count for each token |
| `document_count` | `int` | yes | Number of indexed documents |
| `total_terms` | `int` | yes | Sum of all token occurrences |

## Invariants that M2 depends on

These are tested in `tests/test_tokenizer.py` and `tests/test_vocabulary.py`:

1. **Token order preserved** — `tokens` list is in document order.
2. **No empty tokens** — `""` never appears in `tokens`.
3. **Deterministic** — same input + same config → same output, every time.
4. **Counts consistent** — `sum(term_counts.values()) == token_count == len(tokens)`.
5. **Document frequency ≤ document count** — `df[token] <= document_count` for all tokens.
6. **Complete vocabulary** — every token in any document has an entry in `token_to_id`.

## Non-goals for M1

These belong to later modules:

- No postings lists (M2)
- No ranking scores (M3)
- No phrase-query execution (M5)
- No index persistence format (M2/M8)
