# Hint 1: IDF Computation

## The formula

```
IDF(term) = ln((N - df + 0.5) / (df + 0.5))
```

## Step by step

1. Get the posting list for the term: `index.postings.get(term, [])`
2. `df` = length of the posting list (how many documents contain this term)
3. `N` = `index.document_count`
4. If the posting list is empty (term not in index), return `0.0`
5. Compute the fraction: `(N - df + 0.5) / (df + 0.5)`
6. Take the natural log: `math.log(...)` — this is `ln`, not `log10`

## Common mistakes

- Using `log10` instead of `math.log` (natural log)
- Forgetting the `+0.5` smoothing terms
- Returning a non-zero value when the term is not in the index
- Using `total_terms` instead of `document_count` for N
