# Movies Dataset

150 movie plot summaries for the Part 1 ceremony script.

## Format

**movies.csv** — doc_id, title, text (40-120 word plot descriptions)
**queries.csv** — 25 search queries (20 keyword-friendly, 5 semantic)
**qrels.csv** — ESCI-style relevance judgments (E/S/C/I labels). Uses `product_id`
column (not `doc_id`) to match the ESCI format that the evaluation loader expects.

For M5, this folder also includes structured-query audit assets:

- `structured_queries.csv` / `structured_qrels.csv` — mixed structured profile
- `structured_queries_strict.csv` / `structured_qrels_strict.csv` — strict-intent subset
- `structured_queries_broad.csv` / `structured_qrels_broad.csv` — broad-topic subset
- `STRUCTURED-AUDIT.md` — overview of the M5 profile
- `STRUCTURED-AUDIT-SPLIT.md` — why the profile is split
- `STRUCTURED-AUDIT-RESULTS.md` — mixed-profile findings
- `STRUCTURED-AUDIT-SPLIT-RESULTS.md` — strict vs broad findings

## Usage

This dataset is used by `scripts/ceremony.py` to demonstrate your complete
M0-M4 search pipeline. You can also use it with the CLI directly:

```
python -m indexzero index --csv data/movies/movies.csv --text-column text --doc-id-column doc_id --output movies_index.json
python -m indexzero search --index movies_index.json --query "space adventure"
python -m indexzero eval --index movies_index.json --qrels data/movies/qrels.csv --queries data/movies/queries.csv
```

For M5, compare plain lexical search and structured search explicitly:

```
python -m indexzero search-structured --csv data/movies/movies.csv --text-column text --doc-id-column doc_id --query "\"human world\""
python -m indexzero eval --index C:\Learn\IndexZero\movies_index.json --qrels data/movies/structured_qrels_strict.csv --queries data/movies/structured_queries_strict.csv --k 5 --top-k 5
python -m indexzero eval-structured --csv data/movies/movies.csv --text-column text --doc-id-column doc_id --qrels data/movies/structured_qrels_strict.csv --queries data/movies/structured_queries_strict.csv --k 5 --top-k 5
```

The strict and broad audit splits are useful for teaching different lessons:

- strict-intent queries show when phrase/proximity/boolean constraints can fix top-ranked mistakes
- broad-topic queries show when explicit syntax can become stricter than the user's real intent

## About the data

Factual plot descriptions written for educational use. Covers a mix of
genres and origins including Hollywood, Bollywood, Japanese animation,
Korean, French, and other international films.
