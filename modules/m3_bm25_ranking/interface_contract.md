# M3 -> M4 Interface Contract

M4 (Evaluation) consumes the output of M3 directly. This contract defines what M4 can rely on.

## search contract

`search(query_terms, index, config, top_k) -> list[SearchResult]` returns:

| Property | Type | Guaranteed |
|---|---|---|
| Each element | `SearchResult(doc_id, score)` | yes |
| Length | `<= top_k` | yes |
| Order | score descending, doc_id ascending for ties | yes |
| Score type | `float` (can be negative) | yes |
| Empty query | `[]` | yes |
| No matches | `[]` | yes |

## ScorerConfig contract

| Field | Type | Default | Meaning |
|---|---|---|---|
| `k1` | `float` | 1.2 | tf saturation control |
| `b` | `float` | 0.75 | length normalization control |

## What M4 needs from search results

For each labeled query in the evaluation set, M4 will:

1. Call `search(query_terms, index, config, top_k)` to get ranked results
2. Compare the returned `doc_id` list against ground-truth relevance judgments
3. Compute metrics: precision@k, recall@k, MRR, nDCG

M4 depends on:
- **Deterministic results** — same query + same index + same config = same ranking, always
- **Score ordering** — results are pre-sorted, M4 does not re-sort
- **doc_id stability** — doc_ids match those in the relevance judgment file

## Invariants that M4 depends on

1. **Deterministic ranking** — identical inputs produce identical output order.
2. **Score monotonicity** — higher-scored documents appear before lower-scored ones.
3. **Complete coverage** — every document containing at least one query term is considered for ranking (not just a random sample).
4. **top_k respected** — result list never exceeds top_k length.

## Non-goals for M3

These belong to later modules:

- No relevance judgments or ground truth (M4)
- No query parsing or expansion (M5)
- No phrase or proximity scoring (M5)
- No learned parameters or tuning (M4/M7)
- No hybrid scoring with embeddings (M6)
