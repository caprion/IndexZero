# Hint 2: Document metadata

## Symptom
Tests fail on document_lengths, document_count, or total_terms checks.

## What InvertedIndex needs beyond postings

The postings dict is the core, but BM25 (M3) also needs:
- **document_lengths**: how many tokens each document has
- **document_count**: how many documents total
- **total_terms**: sum of all document token counts

## Where the data comes from

Each `TokenizedDocument` from M1 has a `.token_count` property that gives the total tokens. Use it:

```python
document_lengths[doc.doc_id] = doc.token_count
```

Then `document_count = len(documents)` and `total_terms = sum(document_lengths.values())`.

## Why this matters

BM25 normalizes scores by document length. A 6-token document with 1 mention of "bluetooth" is more focused than an 18-token document with 1 mention. Without accurate lengths, ranking breaks.
