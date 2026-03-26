# Hint 1: Precision@k and Recall@k

## The formulas

```
P@k = |{relevant docs in top k}| / k
R@k = |{relevant docs in top k}| / |{all relevant in qrels}|
```

## Step by step (both metrics share the first 3 steps)

1. Build a set of relevant doc_ids from judgments: `{j.doc_id for j in judgments if j.relevance >= relevance_threshold}`
2. Slice the results to top-k: `results.doc_ids[:k]`
3. Count how many of the top-k are in the relevant set

### For precision:

4. Divide by `k` (not by `len(results.doc_ids[:k])`)
5. Return the result — it will be in [0.0, 1.0]

### For recall:

4. Count the total number of relevant docs: `len(relevant_set)`
5. If total relevant is 0, return `1.0` (vacuously true — nothing to miss)
6. Divide count-found by total-relevant

## Common mistakes

- Dividing precision by `len(top_k)` instead of `k` — when there are fewer results than k, precision should decrease
- Forgetting the vacuous-true case in recall (0 relevant -> return 1.0, not division by zero)
- Building the relevant set from results instead of from judgments
- Not treating unjudged docs as grade 0 — if a doc_id is not in judgments, it is not relevant
