# Part 1 Ceremony

You have completed M0 through M4. Your search engine can tokenize text,
build an inverted index, rank results with BM25, and measure its own quality.

This ceremony runs your entire pipeline on a dataset of 150 movie plot
summaries and shows you what it can do.

## Prerequisites

All four modules must be implemented and passing their tests:

- M1: `tokenize_text`, `tokenize_document`, `build_vocabulary`
- M2: `build_index`, `lookup` (and `save_index`/`load_index` if you did the bonus)
- M3: `score_document`, `search`
- M4: `precision_at_k`, `recall_at_k`, `reciprocal_rank`, `ndcg_at_k`, `evaluate`

## How to run

From the repository root:

```
python scripts/ceremony.py
```

## What happens

**Act 1 — The Feeling.** Three keyword searches on movie plots. You see the
top results with movie titles. This is the visceral proof: your code found
the right movies.

**Act 2 — The Proof.** Full evaluation across 25 judged queries. You see
P@5, R@5, MRR, and nDCG@5 — the same metrics you implemented in M4, now
measuring your own search engine. The output includes a plain-English
interpretation of what the numbers mean.

**Act 3 — The Gap.** Three queries where BM25 struggles. "Feel-good movie
for a rainy day" gets tokenized to terms like "feel", "good", "movie",
"rainy", "day" — BM25 matches those words in plot summaries but cannot
grasp the emotional intent. You will see what relevant movies exist and
how few BM25 actually finds. This is why Part 2 exists.

## What comes next

M5-M9 take your engine from "finds things" to "understands things":

| Module | What it adds |
|---|---|
| M5 | Query processing — spelling, expansion, rewriting |
| M6 | Vector search — embeddings and approximate nearest neighbors |
| M7 | Hybrid retrieval — combining BM25 and vectors |
| M8 | Index pipeline — updates, deletes, segment merges |
| M9 | The full system — a search API you can demo |

## Searching your own data

The ceremony uses the movie dataset, but your indexer works with any CSV
that has a `doc_id` column and a `text` column:

```
python -m indexzero index --csv your_data.csv --text-column text --doc-id-column doc_id --output my_index.json
python -m indexzero search --index my_index.json --query "your search terms"
```

You will build proper file ingestion (folders of .txt, .md, and other
formats) in M8.
