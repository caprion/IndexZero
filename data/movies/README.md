# Movies Dataset

150 movie plot summaries for the Part 1 ceremony script.

## Format

**movies.csv** — doc_id, title, text (40-120 word plot descriptions)
**queries.csv** — 25 search queries (20 keyword-friendly, 5 semantic)
**qrels.csv** — ESCI-style relevance judgments (E/S/C/I labels). Uses `product_id`
column (not `doc_id`) to match the ESCI format that the evaluation loader expects.

## Usage

This dataset is used by `scripts/ceremony.py` to demonstrate your complete
M0-M4 search pipeline. You can also use it with the CLI directly:

```
python -m indexzero index --csv data/movies/movies.csv --text-column text --doc-id-column doc_id --output movies_index.json
python -m indexzero search --index movies_index.json --query "space adventure"
python -m indexzero eval --index movies_index.json --qrels data/movies/qrels.csv --queries data/movies/queries.csv
```

## About the data

Factual plot descriptions written for educational use. Covers a mix of
genres and origins including Hollywood, Bollywood, Japanese animation,
Korean, French, and other international films.
