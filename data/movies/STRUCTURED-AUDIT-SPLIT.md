# Structured Audit Split

The mixed structured audit profile is useful, but it teaches two different things at once.

To make that clearer for students, the profile is split into:

- `structured_queries_strict.csv` / `structured_qrels_strict.csv`
- `structured_queries_broad.csv` / `structured_qrels_broad.csv`

## Strict-intent subset

These queries are best interpreted literally. The user likely wants the exact phrase, the explicit boolean combination, or the close proximity relation.

Examples:

- `"spirit world"`
- `"space ranger"`
- `"witness protection"`
- `time NEAR/3 dilation`
- `great NEAR/2 shark`

For this subset, M5 should usually look clearly better than plain BM25 because the structured syntax matches the likely user intent.

## Broad-topic subset

These queries still use structured syntax, but a user might plausibly accept broader related documents.

Examples:

- `"artificial intelligence"`
- `crime AND family`
- `"remote village"`
- `organized AND crime`
- `"human population"`

For this subset, M5 can become stricter than the qrels want. That is not necessarily a bug. It is a reminder that syntax and intent are not always identical.

## Teaching goal

This split helps students see two different lessons:

1. Query structure can improve retrieval when the structure really is the intent.
2. Query structure can overconstrain retrieval when the real user intent is broader than the syntax suggests.
