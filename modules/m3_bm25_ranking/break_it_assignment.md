# M3 Break-It Assignment

Introduce each bug below into your working scorer, observe how it changes behavior, then revert it. Write down what you observe.

**How to verify:** After introducing each bug, run the specific tests listed. They should fail. If they don't, think about why — some bugs are sneakier than others.

## Bug 1: Reverse the IDF fraction

In `compute_idf`, swap the numerator and denominator:

```python
# Wrong: 
math.log((df + 0.5) / (N - df + 0.5))
```

Run `search(["bluetooth"], index, config)` and `search(["for"], index, config)`.

What changes? Why? ___

**Tests that catch this:** `test_rare_term_higher_than_common`, `test_negative_idf_for_common_term`

## Bug 2: Remove length normalization

In `score_bm25`, simplify the denominator:

```python
# Wrong: ignore document length entirely
denominator = tf + config.k1
```

Search for "phone" across documents of different lengths.

Which documents move up? Which move down? Why? ___

**Tests that catch this:** `test_shorter_doc_scores_higher_same_tf`, `test_b_zero_ignores_length`

## Bug 3: Linear tf (remove saturation)

Replace the BM25 tf component with raw tf * IDF:

```python
# Wrong: no saturation
return idf * tf
```

Find a document where a term appears 3+ times. How much does its score change compared to the correct formula?

What is saturation protecting against? ___

**Tests that catch this:** `test_tf_saturation`, `test_exact_value_known_fixture`

## Bug 4: Integer division

Add a premature int() cast:

```python
# Wrong: truncate intermediate result
denominator = int(tf + config.k1 * (1 - config.b + config.b * dl / avgdl))
```

Run the same search with and without the cast. Do rankings change?

Why is ranking math sensitive to small differences? ___

**Tests that catch this:** `test_exact_value_known_fixture` (may or may not catch this depending on values — try it)

## Bug 5: Max instead of sum

In `search`, take the maximum per-term score instead of the sum:

```python
# Wrong: only the best-matching term counts
scores[doc_id] = max(scores.get(doc_id, 0.0), score)
```

Compare `search(["samsung", "galaxy"], ...)` with sum vs max.

Which documents gain rank? Which lose? What does this tell you about multi-term queries? ___

**Tests that catch this:** `test_multi_term_increases_score`, `test_duplicate_query_terms_count_twice`
