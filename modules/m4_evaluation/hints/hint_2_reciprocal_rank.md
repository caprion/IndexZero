# Hint 2: Reciprocal Rank

## The formula

```
RR = 1 / rank_of_first_relevant
```

Rank is 1-indexed. If no relevant result, return 0.0.

## Step by step

1. Build a set of relevant doc_ids from judgments: `{j.doc_id for j in judgments if j.relevance >= relevance_threshold}`
2. Iterate through `results.doc_ids` using `enumerate`:
   ```python
   for i, doc_id in enumerate(results.doc_ids):
   ```
3. If `doc_id` is in the relevant set, return `1.0 / (i + 1)`
   - `i` is 0-indexed, but rank is 1-indexed, so add 1
4. If you finish the loop without finding a relevant doc, return `0.0`

## Common mistakes

- Off-by-one: returning `1.0 / i` instead of `1.0 / (i + 1)` — this crashes at position 0 and gives wrong values everywhere else
- Checking all results instead of stopping at the first relevant — only the first one matters
- Using the relevance grade directly instead of checking against the threshold
- Iterating over judgments instead of over results — you need the rank from the result list
