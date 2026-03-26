# IndexZero

Build a search engine from scratch. Ten modules, one codebase that grows.

You start with raw text and end with a working search API. Along the way you build a tokenizer, an inverted index, a BM25 scorer, an eval harness, vector retrieval, and hybrid search. Each module feeds the next. Your M1 design choices show up again in M3 scoring — for better or worse.

## Quick start

```bash
git clone https://github.com/caprion/IndexZero.git
cd IndexZero
python -m venv .venv

# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

pip install -e ".[dev]"
pytest tests/ -v
```

You should see many failing tests and a few passing CLI tests. That's correct — each failing test tells you what to implement. The failures all say `NotImplementedError`, pointing to the exact functions.

Start with M0: open `modules/m0_ranking_audit/README.md`.

## Module map

| Module | Name | What you build | Core concept |
|---|---|---|---|
| M0 | The Problem | Ranking audit | Search is ranking, not lookup |
| M1 | Text Processing | Tokenizer + vocabulary | Normalization choices have consequences |
| M2 | The Index | Inverted index | Postings lists and lookup cost |
| M3 | Ranking | BM25 scorer | Term weighting and document length |
| M4 | Did It Work? | Eval harness | nDCG, MRR, precision@k |
| M5 | Smarter Queries | Query processor | Boolean, phrase, proximity |
| M6 | Meaning, Not Words | Vector retrieval | Semantic similarity |
| M7 | Both Together | Hybrid retrieval | Fusion and reranking |
| M8 | Keeping It Alive | Index pipeline | Updates, deletes, segment merges |
| M9 | The Full System | Search API | End-to-end retrieval |

## Repository layout

```
IndexZero/
├── src/indexzero/                  <- your code lives here
│   ├── __init__.py
│   ├── __main__.py                <- CLI: tokenize, vocab, index, lookup, search, eval
│   ├── text_processing/           <- M1: tokenizer + vocabulary
│   │   ├── contracts.py           <- data shapes (given, don't edit)
│   │   ├── tokenizer.py           <- implement this
│   │   └── vocabulary.py          <- implement this
│   ├── indexing/                   <- M2: inverted index
│   │   ├── contracts.py
│   │   ├── serialization.py       <- JSON helpers (given, don't edit)
│   │   └── indexer.py             <- implement this
│   ├── scoring/                   <- M3: BM25 ranking
│   │   ├── contracts.py
│   │   └── scorer.py              <- implement this
│   └── evaluation/                <- M4: search quality metrics
│       ├── contracts.py
│       ├── qrels_io.py            <- CSV helpers (given, don't edit)
│       └── metrics.py             <- implement this
├── tests/                         <- one test file per module
├── data/
│   ├── flipkart_titles_tiny.csv   <- 8 rows for unit tests
│   ├── flipkart_titles_500.csv    <- 500 rows for assessment exercises
│   ├── amazon_esci_sample/        <- 40 products, 20 queries, 100 judgments
│   └── movies/                    <- 150 movie plots for Part 1 ceremony
├── modules/                       <- module guides, hints, assessment artifacts
│   ├── m0_ranking_audit/
│   ├── m1_text_processing/
│   ├── m2_inverted_index/
│   ├── m3_bm25_ranking/
│   ├── m4_evaluation/
│   └── part1_ceremony/            <- celebrate completing Part 1
├── scripts/
│   └── ceremony.py                <- Part 1 ceremony: run your full pipeline
├── pyproject.toml
├── Makefile
└── .github/workflows/test.yml     <- CI: pytest on push
```

## CLI

`python -m indexzero` runs the package as a command-line tool. Once you implement the tokenizer:

```bash
# Tokenize a single string
python -m indexzero tokenize --text "Nike Running Shoes for Men"

# Build vocabulary from the tiny dataset
python -m indexzero vocab --csv data/flipkart_titles_tiny.csv --text-column title
```

After completing M0-M4, run the Part 1 ceremony to see your full pipeline in action:

```bash
python scripts/ceremony.py
```

## Requirements

- Python 3.11+
- No external dependencies (stdlib only)
- pytest for tests (`pip install -e ".[dev]"`)

