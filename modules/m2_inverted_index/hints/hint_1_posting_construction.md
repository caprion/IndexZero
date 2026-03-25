# Hint 1: Posting list construction

## Symptom
Your posting lists have multiple entries for the same document, or term frequencies don't match.

## The key insight
Each document has `term_counts` -- a Counter that already tells you how many times each term appears. You don't need to iterate over the raw `tokens` list. Use `term_counts.items()` to get (term, count) pairs.

## Common mistake
Iterating over `doc.tokens` and appending a new Posting for each token occurrence:
```python
# WRONG: creates one Posting per occurrence, not per document
for token in doc.tokens:
    postings[token].append(Posting(doc_id=doc.doc_id, term_frequency=1))
```

## Better approach
Iterate over the already-aggregated counts:
```python
for term, count in doc.term_counts.items():
    # One Posting per (term, document) pair
    ...
```

This gives you exactly one Posting per document per term, with the correct frequency.
