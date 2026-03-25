# M2 -- The Index

## You are here

```
M0  Ranking Audit          (done -- observation, no code)
M1  Text Processing        (done -- tokenizer + vocabulary)
>>> M2  The Index           (you are here)
M3  Ranking                (next -- BM25 scoring)
M4  Did It Work?           (eval harness)
M5  Smarter Queries        (phrase, proximity)
M6  Meaning, Not Words     (vectors)
M7  Both Together          (hybrid retrieval)
M8  Keeping It Alive       (index updates)
M9  The Full System        (search API)
```

## The gap

Your tokenizer works. You can turn any product title into tokens and build corpus-level vocabulary statistics. But try answering this question:

> Which documents contain the word "bluetooth"?

Right now, your only option is to tokenize every document and check each one:

```python
matches = []
for doc in all_500_documents:
    if "bluetooth" in doc.term_counts:
        matches.append(doc.doc_id)
```

With 500 documents, that scans 500 objects per query.
With 5 million documents, that's 5 million scans. Every single time.

Now run 20 queries. That's 100 million scans.

This is called a **linear scan**, and it's why no real search engine works this way. The fix is a data structure that inverts the question: instead of asking "what tokens does this document have?", ask "which documents have this token?"

That data structure is the **inverted index**, and you build it in this module.

## What you build

Two functions:

| Function | What it does |
|----------|-------------|
| `build_index(documents)` | Turn tokenized documents into an inverted index |
| `lookup(index, term)` | Retrieve the posting list for a single term |

**Optional bonus** (after core tests pass):

| Function | What it does |
|----------|-------------|
| `save_index(index, path)` | Serialize the index to a JSON file |
| `load_index(path)` | Deserialize the index from a JSON file |

## Files to edit

- `src/indexzero/indexing/indexer.py` -- implement your functions here

## Files to read (don't edit)

- `src/indexzero/indexing/contracts.py` -- data shapes: `Posting`, `InvertedIndex`
- `src/indexzero/indexing/serialization.py` -- JSON helpers (given, for bonus exercise)
- `modules/m2_inverted_index/interface_contract.md` -- what M3 expects from your index

## Glossary

**Inverted index**: A mapping from terms to document lists. "Inverted" because it flips the document-to-terms relationship into a terms-to-documents one.

**Posting**: A single entry recording that a term appears in a document, with its frequency. ("Posting" is the traditional IR term -- think of it as a note on a bulletin board saying "this term was found here.")

**Posting list**: All the postings for one term -- the full list of documents containing it.

**Document frequency (df)**: How many documents contain a term. Computable from the posting list: `df = len(index.postings[term])`.

**Term frequency (tf)**: How many times a term appears in one document. Stored in each Posting.

**Document length**: Total token count for a document. Needed by BM25 (M3) for length normalization.

## Python concepts used

- `dict[str, list[...]]` -- mapping with list values
- Iterating over `Counter` items: `for term, count in doc.term_counts.items()`
- Sorting: `list.sort(key=lambda p: p.doc_id)`
- `@property` on a frozen dataclass -- `average_document_length` is computed, not stored

## Recommended approach

### Phase 0: Feel the pain

Before writing any code, run this experiment. In a Python REPL or notebook:

1. Tokenize all 500 documents (using your M1 tokenizer).
2. For each of these 20 terms, scan all 500 documents to find matches:
   `bluetooth, samsung, nike, shoes, laptop, earbuds, men, women, 5g, phone,
    bottle, running, ram, 128gb, cotton, camera, steel, wireless, pack, litre`
3. Count: how many documents did you examine total? (Answer: 10,000.)

That's 10,000 document inspections for 20 queries. The inverted index does it in 20 dictionary lookups.

### Phase 1: Build the simplest index

Implement `build_index`. The core is a dict of lists:

- For each document, for each term in that document, append a `Posting` to that term's list.
- Record each document's length in `document_lengths`.

Start simple. Run `pytest tests/test_indexer.py::TestBuildIndex -v` after each change.

### Phase 2: Add determinism and metadata

Your posting lists should be sorted by `doc_id` (so output is deterministic). Also populate `document_count` and `total_terms`.

Run the full test suite: `pytest tests/test_indexer.py -v`

### Phase 3: Use it

Implement `lookup`. This should be a short function. Then try it in a Python REPL:

```python
from indexzero.text_processing import TokenizerConfig, tokenize_document
from indexzero.indexing import build_index, lookup

# Tokenize a few docs (using your M1 implementation)
config = TokenizerConfig()
docs = [
    tokenize_document("fk-001", "Samsung Galaxy M14 5G 128GB Blue", config),
    tokenize_document("fk-002", "Nike Running Shoes for Men", config),
    tokenize_document("fk-003", "Boat Bluetooth Earbuds with Mic", config),
]

index = build_index(docs)
print(f"Unique terms: {len(index.postings)}")
print(f"Avg doc length: {index.average_document_length:.1f}")

# The payoff: instant lookup vs scanning all documents
print(lookup(index, "bluetooth"))   # one doc
print(lookup(index, "5g"))          # one doc
print(lookup(index, "nonexistent")) # empty list
```

Notice the difference: building the index processes all documents once. But each lookup is instant -- a single dictionary access.

### Phase 4: Inspect and reflect

Look at your index in detail:

- What does a common term's posting list look like? (e.g., "with")
- What does a rare term's posting list look like? (e.g., a specific brand name)
- How many terms are in the index? How many postings total?

Then complete the assessment artifacts in this module folder.

### Optional Phase 5: Persist and use CLI

Implement `save_index` and `load_index` using the helpers in `serialization.py`. Run: `pytest tests/test_index_io.py -v`

Then try the CLI commands (these require save/load to work):

```bash
python -m indexzero index --csv data/flipkart_titles_500.csv --output index.json
python -m indexzero lookup --index index.json --term bluetooth
python -m indexzero lookup --index index.json --term samsung
python -m indexzero lookup --index index.json --term nonexistentterm
```

## Running tests

```bash
# Core tests (build_index + lookup):
pytest tests/test_indexer.py -v

# Bonus tests (save/load round-trip):
pytest tests/test_index_io.py -v

# All tests including M1:
pytest tests/ -v
```

## Assessment artifacts

Complete these after your implementation passes tests:

1. **Decision log** (`decision_log_template.md`) -- justify your design choices
2. **Break-it assignment** (`break_it_assignment.md`) -- intentionally corrupt your index
3. **Consequence chain** (`consequence_chain.md`) -- predict how index choices affect M4 (eval)
