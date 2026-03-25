# M2 -> M3 Interface Contract

M3 (BM25 Ranking) consumes the output of M2 directly. This contract defines what M3 can rely on.

## InvertedIndex contract

The index built by `build_index()` exposes:

| Field | Type | Required | Meaning |
|---|---|---|---|
| `postings` | `dict[str, list[Posting]]` | yes | Term to posting list mapping |
| `document_lengths` | `dict[str, int]` | yes | doc_id to token count |
| `document_count` | `int` | yes | Number of indexed documents |
| `total_terms` | `int` | yes | Sum of all document token counts |
| `average_document_length` | `float` (property) | yes | Computed: total_terms / document_count |

## Posting contract

Each Posting in a posting list exposes:

| Field | Type | Required | Meaning |
|---|---|---|---|
| `doc_id` | `str` | yes | The document this posting refers to |
| `term_frequency` | `int` | yes | Times the term appears in this document |

## lookup contract

`lookup(index, term) -> list[Posting]` returns:
- The posting list for the term if it exists
- An empty list `[]` if the term is not in the index

## What BM25 needs from the index

For each query term, BM25 computes a score per document using:

1. **tf** (term frequency): `posting.term_frequency` from the posting list
2. **df** (document frequency): `len(index.postings[term])` -- number of documents containing the term
3. **dl** (document length): `index.document_lengths[doc_id]` -- token count for the document being scored
4. **avgdl** (average document length): `index.average_document_length`
5. **N** (total documents): `index.document_count`

All five values are available directly from InvertedIndex. No Vocabulary object needed.

## Invariants that M3 depends on

1. **One posting per (term, document)** -- no duplicates in posting lists.
2. **Sorted posting lists** -- by doc_id, deterministic.
3. **Consistent document_lengths** -- matches actual token counts from M1.
4. **Non-zero term frequencies** -- every posting has tf > 0.
5. **Complete coverage** -- every term in any document has an entry in postings.

## Non-goals for M2

These belong to later modules:

- No ranking scores (M3)
- No query parsing or multi-term queries (M3/M5)
- No token positions within documents (M5)
- No vector embeddings (M6)
- No index updates or deletes (M8)
