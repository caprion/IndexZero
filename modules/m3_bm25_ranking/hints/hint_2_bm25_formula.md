# Hint 2: BM25 Formula Structure

## The formula

```
score(t, d) = IDF(t) * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avgdl))
```

## Step by step

1. Look up the term in the index. If not found, return `0.0`
2. Find the posting for this specific `doc_id` in the posting list. If not found, return `0.0`
3. Get `tf` from `posting.term_frequency`
4. Get `dl` from `index.document_lengths[doc_id]`
5. Get `avgdl` from `index.average_document_length`
6. Compute IDF using your `compute_idf` function
7. Compute the numerator: `tf * (k1 + 1)`
8. Compute the denominator: `tf + k1 * (1 - b + b * dl / avgdl)`
9. Return `idf * numerator / denominator`

## Common mistakes

- Forgetting to check if doc_id is in the posting list (not just if the term is in the index)
- Operator precedence: `k1 * (1 - b + b * dl / avgdl)` — make sure the multiplication and division are grouped correctly
- Using integer division somewhere in the chain
- Not reusing your `compute_idf` function (duplicating the IDF logic)
