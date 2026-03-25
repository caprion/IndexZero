# Hint 3: Deterministic output

## Symptom
Tests say posting lists are not sorted by doc_id, or two calls to build_index produce different output.

## Why sorting matters

If you iterate over documents in order and append to posting lists, the order depends on document input order. That's fragile -- reordering the CSV would change your index.

Sort each posting list by `doc_id` after building:

```python
for term in postings:
    postings[term].sort(key=lambda p: p.doc_id)
```

## Why determinism matters

Tests compare two calls to `build_index` with the same input. If output isn't deterministic, those tests fail. Deterministic output also makes debugging easier (same input = same index every time) and is required for reproducible eval scores in M4.
