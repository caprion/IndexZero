# IndexZero

Build a search engine from scratch. Ten modules, one codebase that grows.

You start with raw text and end with a working search API. Along the way you build a tokenizer, an inverted index, a BM25 scorer, an eval harness, vector retrieval, and hybrid search. Each module feeds the next. Your M1 design choices show up again in M3 scoring — for better or worse.

## Quick start (5 minutes)

```bash
# Fork the repo on GitHub first (click "Fork" on the repo page).
# Then clone YOUR fork:
git clone https://github.com/YOUR-USERNAME/IndexZero.git
cd IndexZero

# Check your Python version (need 3.11 or higher):
python --version

python -m venv .venv

# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# Install the project in editable mode with dev tools (pytest):
# -e = live link to your code, . = this directory, [dev] = include pytest
pip install -e ".[dev]"
pytest tests/ -v
```

> **What's a virtual environment?** A venv is an isolated Python folder so this project's packages don't interfere with your other projects. After running `python -m venv .venv`, you'll have a `.venv/` directory. You must *activate* it before every work session — look for `(.venv)` at the start of your terminal prompt.
>
> **Windows PowerShell blocks scripts?** If you see a red error about "execution policy", run this once:
> ```
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Then try `.venv\Scripts\Activate.ps1` again.
>
> **Closed your terminal?** You need to re-activate: `cd IndexZero` then `.venv\Scripts\Activate.ps1` (or `source .venv/bin/activate` on Mac/Linux). If you don't see `(.venv)` in your prompt, the venv isn't active.

You should see about **44 failing tests** and **3 passing** CLI tests. That's correct — each failing test tells you what to implement. The failures all say `NotImplementedError`, pointing to the exact functions.

Start with M1: open `modules/m1_text_processing/README.md`.

## Module map

| Module | Name | What you build | Core concept |
|---|---|---|---|
| M0 | The Problem | Ranking audit | Search is ranking, not lookup |
| **M1** | **Text Processing** | **Tokenizer + vocabulary** | **Normalization choices have consequences** |
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
├── src/indexzero/                  ← your code lives here
│   ├── __init__.py
│   ├── __main__.py                ← CLI entry point
│   └── text_processing/           ← M1: tokenizer + vocabulary
│       ├── contracts.py           ← data shapes (given, don't edit)
│       ├── tokenizer.py           ← implement this
│       └── vocabulary.py          ← implement this
├── tests/                         ← tests ship with the repo
│   ├── conftest.py                ← shared fixtures
│   ├── test_tokenizer.py          ← run these as you work
│   ├── test_vocabulary.py
│   └── test_cli.py
├── data/
│   ├── flipkart_titles_tiny.csv   ← 8 rows for unit tests
│   └── flipkart_titles_500.csv    ← 500 rows for assessment exercises
├── modules/
│   ├── m0_ranking_audit/
│   └── m1_text_processing/        ← module guide + assessment artifacts
│       ├── README.md              ← start here for M1
│       ├── decision_log_template.md
│       ├── break_it_assignment.md
│       ├── consequence_chain.md
│       ├── config_mutations.md
│       ├── observe_prompts.md
│       ├── interface_contract.md
│       └── hints/                 ← open when stuck (5 concept guides)
├── scripts/
│   ├── generate_corpus.py         ← generates the 500-title dataset
│   └── prepare_course_data.py     ← placeholder for ESCI download
├── docs/                          ← course overview page
├── pyproject.toml
├── Makefile
└── .github/workflows/test.yml     ← CI: pytest on push
```

## Design principles

- **Zero to running in 5 minutes.** Fork, venv, install, see failing tests.
- **Tests ship with the skeleton.** You know what "done" looks like before writing any code.
- **AI-assisted implementation is expected.** Understanding is measured through decision logs, break-it assignments, and consequence chains, not whether you typed the code yourself.
- **One codebase grows.** M2 depends on M1's output shape. Your choices carry forward.
- **No Docker, no complex tooling.** Python + pip + pytest. That's it.

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

## Why Python only

Most courses that teach systems concepts through building pick one language and stick with it. IndexZero uses Python because the focus is search, not language mechanics.

Module boundaries use defined data contracts (dataclasses in `contracts.py`) with exact field names and types. If you want to port a component to another language later, the JSON serialization of these contracts is your interface spec. But for the course, stay in Python. M3 can't import M1's vocabulary if they're in different languages.
