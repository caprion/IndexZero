# IndexZero

Build a search engine from scratch. Ten modules, one codebase that grows.

You start with raw text and end with a working search API. Along the way you build a tokenizer, an inverted index, a BM25 scorer, an eval harness, vector retrieval, and hybrid search. Each module feeds the next. Your M1 design choices show up again in M3 scoring — for better or worse.

## Quick start (5 minutes)

```bash
git clone https://github.com/YOUR-USERNAME/IndexZero.git
cd IndexZero
python -m venv .venv

# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

pip install -e ".[dev]"
pytest tests/ -v
```

> **Windows PowerShell blocks scripts?** Run once: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

You should see many failing tests and a few passing CLI tests. That's correct — each failing test tells you what to implement. The failures all say `NotImplementedError`, pointing to the exact functions.

Start with M1: open `modules/m1_text_processing/README.md`.

## Module map

| Module | Name | What you build | Core concept |
|---|---|---|---|
| M0 | The Problem | Ranking audit | Search is ranking, not lookup |
| M1 | Text Processing | Tokenizer + vocabulary | Normalization choices have consequences |
| M2 | The Index | Inverted index | Postings lists and lookup cost |
| **M3** | **Ranking** | **BM25 scorer** | **Term weighting and document length** |
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
│   ├── __main__.py                <- CLI: tokenize, vocab, index, lookup, search
│   ├── text_processing/           <- M1: tokenizer + vocabulary
│   │   ├── contracts.py           <- data shapes (given, don't edit)
│   │   ├── tokenizer.py           <- implement this
│   │   └── vocabulary.py          <- implement this
│   ├── indexing/                   <- M2: inverted index
│   │   ├── contracts.py           <- data shapes (given, don't edit)
│   │   ├── serialization.py       <- JSON helpers (given, don't edit)
│   │   └── indexer.py             <- implement this
│   └── scoring/                   <- M3: BM25 ranking
│       ├── contracts.py           <- data shapes (given, don't edit)
│       └── scorer.py              <- implement this
├── tests/
│   ├── conftest.py                <- shared fixtures
│   ├── test_tokenizer.py          <- M1 tests
│   ├── test_vocabulary.py         <- M1 tests
│   ├── test_indexer.py            <- M2 tests (skip until M1 done)
│   ├── test_index_io.py           <- M2 bonus tests
│   ├── test_scorer.py             <- M3 tests (skip until M2 done)
│   └── test_cli.py
├── data/
│   ├── flipkart_titles_tiny.csv   <- 8 rows for unit tests
│   └── flipkart_titles_500.csv    <- 500 rows for assessment exercises
├── modules/
│   ├── m0_ranking_audit/
│   ├── m1_text_processing/        <- module guide + assessment artifacts
│   │   ├── README.md              <- start here for M1
│   │   └── hints/
│   ├── m2_inverted_index/         <- module guide + assessment artifacts
│   │   ├── README.md              <- start here for M2
│   │   └── hints/
│   └── m3_bm25_ranking/           <- module guide + assessment artifacts
│       ├── README.md              <- start here for M3
│       └── hints/
├── scripts/
│   ├── generate_corpus.py         <- generates the 500-title dataset
│   └── prepare_course_data.py     <- placeholder for ESCI download
├── docs/
├── pyproject.toml
├── Makefile
└── .github/workflows/test.yml     <- CI: pytest on push
```

## CLI

`python -m indexzero` runs the package as a command-line tool (it executes `__main__.py` inside the `indexzero` package). Once you implement the tokenizer:

```bash
# Tokenize a single string
python -m indexzero tokenize --text "Nike Running Shoes for Men"

# Build vocabulary from the tiny dataset
python -m indexzero vocab --csv data/flipkart_titles_tiny.csv --text-column title
```

## Requirements

- Python 3.11+
- No external dependencies (stdlib only)
- pytest for tests (`pip install -e ".[dev]"`)

