# M4 Break-It Assignment

Introduce each bug below into your working metrics, observe how it changes behavior, then revert it. Write down what you observe.

**How to verify:** After introducing each bug, run the specific tests listed. They should fail. If they don't, think about why — some bugs are sneakier than others.

## Bug 1: Remove the log discount in nDCG

In `ndcg_at_k`, remove the positional discount so DCG is just the sum of relevance grades:

```python
# Wrong: no positional discount
dcg += rel  # instead of rel / math.log2(i + 2)
```

Run `ndcg_at_k` on results where a grade-3 doc is at position 1 vs position 10.

What changes? Why does position no longer matter? ___

**Tests that catch this:** `test_position_matters`, `test_exact_value_known`, `test_reversed_ranking_less_than_one`

## Bug 2: Skip IDCG normalization

Return raw DCG instead of normalizing by IDCG:

```python
# Wrong: return DCG directly
return dcg  # instead of dcg / idcg
```

Compute nDCG for a query with grades [3, 2, 1] vs grades [1, 0, 0]. Does the first always score higher?

Why is normalization necessary for comparing across queries? ___

**Tests that catch this:** `test_perfect_ranking_is_one`, `test_ndcg_normalized_range`, `test_exact_value_known`

## Bug 3: Off-by-one in reciprocal_rank

Use 0-indexed rank instead of 1-indexed:

```python
# Wrong: 0-indexed, so first result gives 1/0 -> crash, or 1/(i) instead of 1/(i+1)
return 1.0 / i  # instead of 1.0 / (i + 1)
```

What happens when the first result is relevant? What about the second?

Why does 1-indexed ranking matter for interpreting MRR? ___

**Tests that catch this:** `test_first_position`, `test_third_position`

## Bug 4: Treat unjudged docs as relevant

When looking up a document not in the judgments, default to grade 3 instead of 0:

```python
# Wrong: assume unjudged docs are Exact matches
grade = grade_map.get(doc_id, 3)  # instead of grade_map.get(doc_id, 0)
```

Run precision and nDCG on results that include many unjudged documents.

What happens to precision? What happens to nDCG? Why is the conservative default (0) important? ___

**Tests that catch this:** `test_unjudged_not_relevant`, `test_partial_precision`, `test_ndcg_normalized_range`

## Bug 5: Wrong recall denominator

Divide by k instead of total relevant:

```python
# Wrong: divide by k instead of total relevant
return found / k  # instead of found / total_relevant
```

Compare recall when total_relevant=2 vs total_relevant=20 for the same top-k results.

Why does this make recall and precision identical? What information is lost? ___

**Tests that catch this:** `test_partial_recall`, `test_recall_vs_precision_different`, `test_full_recall`
