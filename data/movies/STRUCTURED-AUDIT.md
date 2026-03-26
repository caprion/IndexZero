# Structured Audit Profile

This file adds a small M5-specific audit profile for the movies dataset.

The original [queries.csv](queries.csv) file is mostly plain lexical search. That is useful for M3 and M4, but it does not really exercise phrase, boolean, or proximity behavior.

These files do:

- `structured_queries.csv`
- `structured_qrels.csv`

## Why this profile exists

M5 should be evaluated on queries that actually require structured lexical retrieval.

Examples:

- exact phrase: `"artificial intelligence"`
- boolean logic: `crime AND family`
- proximity: `mother NEAR/5 daughter`
- exact phrase: `"witness protection"`
- boolean logic: `organized AND crime`
- proximity: `time NEAR/3 dilation`

If you run M5 against only plain keyword queries, structured search should look almost identical to BM25. That is expected. This profile is the targeted check that the new module changes retrieval when query structure is explicit.

## Usage

```bash
python -m indexzero eval \
  --index C:\Learn\IndexZero\movies_index.json \
  --qrels data/movies/structured_qrels.csv \
  --queries data/movies/structured_queries.csv \
  --k 10 --top-k 10

python -m indexzero eval-structured \
  --csv data/movies/movies.csv \
  --text-column text \
  --doc-id-column doc_id \
  --qrels data/movies/structured_qrels.csv \
  --queries data/movies/structured_queries.csv \
  --k 10 --top-k 10
```

## Notes

- This is a targeted teaching profile, not a broad benchmark.
- Relevance judgments are intentionally sparse and focused on the structured behavior being tested.
- Exact scores matter less than the directional comparison between plain search and structured search.
