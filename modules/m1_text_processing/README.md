# M1 — Text Processing

M1 is where search stops feeling magical and starts feeling mechanical.

You take raw product titles and turn them into a token stream that later modules can index, score, and evaluate. The point is not to produce the perfect tokenizer on day one. The point is to discover that every normalization choice creates downstream consequences.

## Glossary

Terms used throughout this module:

- **Token** — one word-unit after processing. `"running"` is a token. So is `"8gb"`.
- **Corpus** — the full collection of documents you're searching over.
- **Vocabulary** — the set of unique tokens across the corpus, with counts.
- **Stopword** — a very common word (`the`, `for`, `is`) that may not help distinguish documents.
- **Stemming** — reducing words to a root form. `"running"` becomes `"run"` or `"runn"`.
- **Document frequency** — how many documents contain a given token.
- **Collection frequency** — how many times a token appears across all documents combined.
- **Hapax legomenon** — a token that appears in only one document. Most vocabularies are full of these.
- **Invariant** — a rule that must always be true. Example: `len(tokens) == sum(term_counts.values())`. Any output that violates an invariant is a bug. Tests check invariants automatically.
- **Deterministic** — same input always produces the same output. No randomness involved. Your tokenizer must be deterministic.

## Python concepts used in this module

M1 code uses a few Python features that may be new to you. Quick orientation:

**Dataclasses.** The `contracts.py` file defines data shapes using `@dataclass(frozen=True)`. Think of a dataclass as a container with named slots. When you write `TokenizerConfig(lowercase=True)`, Python creates an object with a `lowercase` field set to `True`. `frozen=True` means instances cannot be modified after creation. `field(default_factory=dict)` creates a fresh empty dict for each new instance instead of sharing one across all instances.

To create a `TokenizedDocument`, pass all fields by name:
```python
from collections import Counter
doc = TokenizedDocument(
    doc_id="fk-001",
    normalized_text="hello world",
    tokens=["hello", "world"],
    term_counts=Counter(["hello", "world"]),
)
```

**Type hints.** You'll see `list[str]`, `dict[str, int]`, `Counter[str]`, and `X | None` throughout. These are annotations that describe the expected types. They do not affect how your code runs. You do not need to "make the types work." Just write your logic and return the right data. `Counter[str]` is a `collections.Counter` keyed by strings — it counts how many times each token appears. Create one with `Counter(your_list)`. The `X | None` syntax (Python 3.10+) means "either X or None."

**pytest and fixtures.** Tests use pytest, not unittest. Key difference: test functions receive data via *fixtures* — functions decorated with `@pytest.fixture` in `conftest.py`. pytest finds `conftest.py` automatically. If you see `def test_foo(self, sample_text)`, pytest automatically calls the `sample_text()` fixture defined in `conftest.py` and passes its return value. You do not call it yourself. See [pytest: fixtures](https://docs.pytest.org/en/stable/fixture.html).

**`pip install -e ".[dev]"`** — this appears in the setup steps. `-e` means editable install (changes to your code take effect immediately without reinstalling). `.` means the project in the current directory. `[dev]` means also install the dev extras defined in `pyproject.toml` (just pytest). If this command fails, check that your virtual environment is activated and you're in the project root.

## What you build

Two things:

1. **A tokenizer** that turns raw text into an ordered list of tokens.
2. **A vocabulary builder** that aggregates token statistics across the corpus.

That's it. Two files, four functions.

## Files to edit

```
src/indexzero/text_processing/tokenizer.py    ← implement normalize_text, tokenize_text, tokenize_document
src/indexzero/text_processing/vocabulary.py   ← implement build_vocabulary
```

Files you should **read but not edit**:

```
src/indexzero/text_processing/contracts.py    ← TokenizerConfig, TokenizedDocument, Vocabulary
src/indexzero/text_processing/__init__.py     ← public exports
```

## What "done" looks like

All tests pass:

```bash
pytest tests/test_tokenizer.py tests/test_vocabulary.py -v
```

The CLI works:

```bash
python -m indexzero tokenize --text "Nike Revolution Running Shoes for Men"
python -m indexzero vocab --csv data/flipkart_titles_tiny.csv --text-column title
```

## Getting started (5 minutes)

```bash
git clone <your-fork>
cd IndexZero
python -m venv .venv

# Windows PowerShell:
.venv\Scripts\Activate.ps1

# Linux / macOS:
source .venv/bin/activate

pip install -e ".[dev]"
pytest tests/ -v
```

You should see failing tests — about 44 failures and 3 passing CLI tests. That's correct. Each failing test tells you what to implement. The `NotImplementedError` messages point to the exact functions.

## Recommended approach

### Phase 1 — Naive first pass

Build the simplest thing that could work:

- Lowercase the input
- Split on whitespace
- Count tokens

Run `pytest tests/test_tokenizer.py -v`. Some tests will pass.

### Phase 2 — Repair with intent

Improve the pipeline by making explicit choices about:

- Punctuation and separators (slashes, hyphens, underscores)
- Numeric boundaries (`8GB` → `8` `gb`?)
- Unicode normalization
- Stopwords (which ones? why?)
- Stemming (what strategy? what breaks?)

**Suffix stemming** means stripping common English endings (`-ing`, `-ed`, `-er`, `-s`, `-ly`) to group word variants together. `"running"` should become `"run"`, not `"runn"`. The trade-off: aggressive stemming merges words that should stay separate (`"universal"` and `"university"`).

**Stuck on a step?** The `hints/` folder has five files covering the hardest parts (accent stripping, numeric boundaries, stemming convergence, separator strategy, Unicode normalization). Try to solve it yourself first — then open the hint if you're genuinely stuck. Record which hints you used in your decision log.

**Every change should be justified in your decision log** (`decision_log_template.md`).

### Phase 3 — Vocabulary builder

Once your tokenizer passes its tests, implement `build_vocabulary` in `vocabulary.py`. This aggregates token statistics across the whole corpus.

Run `pytest tests/test_vocabulary.py -v`.

### Phase 4 — Inspect and reflect

Use the CLI to inspect your output:

```bash
python -m indexzero tokenize --text "HP 15s Ryzen 5 Laptop 16GB RAM 512GB SSD"
python -m indexzero vocab --csv data/flipkart_titles_tiny.csv
```

Then complete:

- `decision_log_template.md` — your design choices with evidence
- `break_it_assignment.md` — find inputs that break your tokenizer
- `consequence_chain.md` — predict what happens in M3 if you change config

## Learning objectives

By the end of M1, you should be able to:

1. Explain why text preprocessing is part of the retrieval system, not a cosmetic cleanup step.
2. Compare tokenization decisions in terms of vocabulary size, matching behavior, and downstream index quality.
3. Build a repeatable text-processing pipeline that turns raw strings into normalized tokens.
4. Write down design decisions in a way that can be defended when later modules expose their trade-offs.

## What you'll get wrong first (and that's fine)

- "Whitespace splitting is good enough."
- "Lowercasing is harmless in every case."
- "Removing stopwords always improves search."
- "A tokenizer is a library choice, not a system decision."

M1 makes these mistakes visible and concrete.

## Connection to M2

M2 (Inverted Index) will consume your `TokenizedDocument` and `Vocabulary` objects directly. The interface contract is documented in `interface_contract.md`.

If your M1 output is fuzzy or inconsistent, M2 becomes a cleanup module instead of an indexing module. Don't let that happen.

## Assessment artifacts

| Artifact | File | What it measures |
|---|---|---|
| Decision log | `decision_log_template.md` | Can you justify your choices with evidence? |
| Break-it | `break_it_assignment.md` | Can you find where your own code fails? |
| Consequence chain | `consequence_chain.md` | Can you predict cross-module effects? |
| Config mutations | `config_mutations.md` | Do you understand what each config flag does? |
