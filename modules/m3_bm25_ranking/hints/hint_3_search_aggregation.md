# Hint 3: Search Aggregation

## The idea

For each query term, BM25 produces a score per document. The total document score is the SUM of all per-term scores.

## Step by step

1. Create an empty dict to accumulate scores: `scores = {}`
2. For each term in `query_terms`:
   a. Get the posting list from the index
   b. For each posting in the list, call `score_bm25(term, posting.doc_id, ...)`
   c. Add the score to `scores[doc_id]`
3. Sort by score descending, then doc_id ascending for ties
4. Return the top `top_k` results as `SearchResult` objects

## Sorting

```python
sorted(scores.items(), key=lambda pair: (-pair[1], pair[0]))
```

This sorts by negative score (so highest first), then by doc_id alphabetically.

## Common mistakes

- Using `max` instead of sum (only the best term counts, others ignored)
- Intersecting posting lists instead of unioning (only docs with ALL terms appear)
- Forgetting to handle terms not in the index (they should contribute nothing, not crash)
- Not respecting `top_k` (returning all results instead of truncating)
- Sorting only by score without a tie-breaker (non-deterministic ordering)
