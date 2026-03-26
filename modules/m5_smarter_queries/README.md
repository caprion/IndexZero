# M5: Smarter Queries

## You are here

```
M0  Ranking Audit          done — observation, no code
M1  Text Processing        done — tokenizer + vocabulary
M2  The Index              done — inverted index + lookup
M3  Ranking                done — BM25 scorer
M4  Did It Work?           done — evaluation harness
>>> M5  Smarter Queries    you are here
M6  Meaning, Not Words     next — vector retrieval
M7  Both Together          later — hybrid retrieval
```

Up to M4, your search engine treats a query as a bag of terms. That works for many cases. But users do not always mean "find documents containing these words somewhere."

Sometimes they mean:

- these two ideas must both be present
- this exact phrase matters
- these words should occur near each other

M5 teaches the first real layer of query understanding. It does **not** make the engine semantic. It makes the engine structurally aware.

That distinction matters.

M5 is the bridge between:

- **M3/M4** — lexical ranking and evaluation
- **M6/M7** — semantic retrieval and hybrid systems

If M5 grows into synonym expansion, spelling correction, or learned reranking, the course loses its shape. So this module stays narrow on purpose.

## Files to edit

| File | Action |
|---|---|
| `src/indexzero/query_language/parser.py` | Implement query parsing |
| `src/indexzero/query_language/contracts.py` | Read or lightly extend AST/query contracts |
| `src/indexzero/query_processing/positional_index.py` | Build positional postings |
| `src/indexzero/query_processing/executor.py` | Execute boolean, phrase, and proximity queries |
| `src/indexzero/__main__.py` | Add CLI entry points for structured search |

Exact file names may shift slightly as the implementation lands, but the architecture should stay the same: **parse -> retrieve/filter -> rank**.

## The idea

M3 gave you ranked lexical retrieval:

1. tokenize the query
2. find matching documents through the inverted index
3. score with BM25
4. sort by score

That model has a blind spot: it ignores structure.

Compare these queries:

- `wireless earbuds`
- `"wireless earbuds"`
- `wireless AND earbuds`
- `wireless NEAR/3 earbuds`

These are not the same request.

The first says "rank documents containing these terms."
The second says "the exact adjacent phrase matters."
The third says "both ideas must be present."
The fourth says "the terms should occur close together, but not necessarily adjacent."

M5 adds that distinction while staying in the lexical world.

## What M5 is for

By the end of this module, you should be able to:

1. Parse a structured query into an internal representation
2. Execute boolean logic using set operations over posting lists
3. Explain why phrase and proximity search need token positions
4. Build a positional extension to your index
5. Reuse BM25 to rank the documents that survive structural filtering

That last point is important: **M5 is still lexical ranking.**

## What M5 is not for

These are explicit non-goals:

- no synonym expansion
- no spelling correction
- no autocomplete or wildcard search
- no query rewriting heuristics
- no learned reranking
- no embeddings
- no semantic similarity search
- no hybrid fusion
- no fielded search syntax
- no weighted query language

Those belong to later modules or a different course entirely.

## Design philosophy

M5 should lay the ground for M6 and beyond without trying to do their work.

That means:

- **M5 adds query structure**
- **M6 adds semantic retrieval**
- **M7 combines lexical and semantic retrieval**

The cleanest architecture is:

1. **Parse** the query into a tree
2. **Retrieve/filter** lexical candidates using boolean logic and positional checks
3. **Rank** the surviving candidates with BM25

That architecture matters because M6 can later add a second retrieval path without rewriting the whole system.

## Scope

M5 supports exactly four query capabilities:

- Boolean operators: `AND`, `OR`, `NOT`
- Parentheses for grouping
- Exact phrase queries: `"wireless earbuds"`
- Simple proximity queries: `wireless NEAR/3 earbuds`

That is enough to teach structured retrieval, positional indexes, and lexical candidate filtering.

It is not enough to become a giant query language. Good.

## Phase 0: See the limitation

Before writing code, compare these three document titles:

1. `Wireless Earbuds with Charging Case`
2. `Wireless Bluetooth Headphones for Travel`
3. `Earbuds for Running with Wireless Connectivity`

For the query `"wireless earbuds"`:

- a bag-of-words BM25 search may return all three
- an exact phrase query should strongly prefer or require document 1

Your current M2/M3 pipeline cannot make that distinction from term frequencies alone. It knows that both words appear. It does **not** know where they appear.

That is the reason M5 exists.

## Phase 1: Boolean retrieval

Start with the part that does **not** require positions.

Implement:

- `term1 AND term2`
- `term1 OR term2`
- `term1 NOT term2`
- parentheses for grouping

Boolean retrieval is a set problem:

- `AND` -> intersection
- `OR` -> union
- `NOT` -> subtraction

This phase teaches that retrieval can be about candidate generation, not just scoring.

Important: boolean retrieval should still feed a ranked result list at the end. Use BM25 to rank the matched documents rather than returning an arbitrary set order.

## Phase 2: Why positions matter

A standard inverted index tells you:

- which documents contain a term
- how often the term appears in each document

It does **not** tell you:

- where in the document the term appears

Phrase and proximity queries need that information.

So M5 should add a **positional index** beside the existing inverted index.

Do not replace the old M2 contract. Extend the system with a second structure.

That keeps M2-M4 stable and makes the learning progression visible:

- M2: postings with document frequency and tf
- M5: postings plus positions

## Phase 3: Positional index

Add positional postings with the minimum extra information needed for phrase and proximity checks.

Recommended shape:

- `doc_id`
- `term_frequency`
- `positions`

Where `positions` is the ordered list of token offsets where the term occurs in that document.

Example:

Document tokens:

```text
["wireless", "earbuds", "with", "wireless", "charging", "case"]
```

For term `wireless`, the positional posting would include:

```text
doc_id="d1", term_frequency=2, positions=[0, 3]
```

## Phase 4: Phrase queries

An exact phrase query like `"wireless earbuds"` should match only documents where:

- both terms appear
- in the same order
- at adjacent positions

This is the first payoff of the positional index.

The phrase query does not need a new ranker. It needs a stricter match condition.

A simple execution model is:

1. get candidate docs containing all phrase terms
2. inspect positions inside each candidate
3. keep docs with a valid contiguous match
4. rank those docs with BM25 using the phrase terms

## Phase 5: Proximity queries

Now relax adjacency without removing positional structure.

For:

```text
wireless NEAR/3 earbuds
```

the engine should match documents where the terms occur within a window of three positions.

Decide and document one rule clearly:

- ordered proximity, or
- unordered proximity

Either is acceptable for the module if the tests and docs are consistent. The simpler teaching path is usually unordered proximity.

## Phase 6: Keep ranking separate

M5 should **not** invent a new scoring model.

Use the structured query to define the candidate set. Then use BM25 to rank the surviving documents.

This separation is the most important architectural decision in the module:

- parsing decides what the user asked for
- matching decides which docs satisfy the structure
- ranking orders those docs

That design becomes even more valuable in M6 and M7.

## Query language

Recommended supported syntax:

- `samsung AND phone`
- `samsung OR nike`
- `phone NOT case`
- `(samsung OR redmi) AND phone`
- `"wireless earbuds"`
- `wireless NEAR/3 earbuds`

Recommended precedence:

1. `NOT`
2. `AND`
3. `OR`

Parentheses override precedence.

If you support all-negative queries like `NOT case`, define the behavior explicitly. The safer first version is to require at least one positive clause at the root.

## Architecture target

Aim for this pipeline:

```text
query text
   ↓
parser
   ↓
query tree / AST
   ↓
lexical candidate retrieval + structural filtering
   ↓
BM25 ranking over matched docs
   ↓
ranked SearchResult list
```

That is the exact handoff shape you want before M6 introduces semantic retrieval.

## Why this sets up M6

After M5, the engine should feel smarter but still obviously lexical.

It should still fail when:

- the right document uses different words
- the query is semantically related but lexically mismatched
- synonyms matter more than exact term overlap

That remaining gap is what M6 solves.

So the emotional outcome of M5 should be:

> "The engine now respects structure. It still does not understand meaning."

Perfect. That is the right bridge into vector retrieval.

## Audit workflow

Do not stop at "the code works." M5 is one of the first modules where the same query can mean different things depending on its structure.

So you should run an explicit audit after implementation.

The movies dataset includes a targeted M5 audit split:

- `data/movies/structured_queries_strict.csv`
- `data/movies/structured_qrels_strict.csv`
- `data/movies/structured_queries_broad.csv`
- `data/movies/structured_qrels_broad.csv`
- `data/movies/STRUCTURED-AUDIT-SPLIT.md`
- `data/movies/STRUCTURED-AUDIT-SPLIT-RESULTS.md`

Use both the plain and structured search paths:

```bash
python -m indexzero eval \
  --index C:\Learn\IndexZero\movies_index.json \
  --qrels data/movies/structured_qrels_strict.csv \
  --queries data/movies/structured_queries_strict.csv \
  --k 5 --top-k 5

python -m indexzero eval-structured \
  --csv data/movies/movies.csv \
  --text-column text \
  --doc-id-column doc_id \
  --qrels data/movies/structured_qrels_strict.csv \
  --queries data/movies/structured_queries_strict.csv \
  --k 5 --top-k 5
```

Then repeat for the broad-topic split:

```bash
python -m indexzero eval \
  --index C:\Learn\IndexZero\movies_index.json \
  --qrels data/movies/structured_qrels_broad.csv \
  --queries data/movies/structured_queries_broad.csv \
  --k 5 --top-k 5

python -m indexzero eval-structured \
  --csv data/movies/movies.csv \
  --text-column text \
  --doc-id-column doc_id \
  --qrels data/movies/structured_qrels_broad.csv \
  --queries data/movies/structured_queries_broad.csv \
  --k 5 --top-k 5
```

## Strict vs broad

The audit is split on purpose because M5 teaches two different ideas.

### Strict-intent queries

These are queries where the structure is probably the intent:

- `"spirit world"`
- `"space ranger"`
- `"witness protection"`
- `time NEAR/3 dilation`
- `great NEAR/2 shark`
- `"human world"`
- `"family moves"`

For these, M5 should usually look better because the structure is doing real retrieval work.

### Broad-topic queries

These are queries where the syntax is structured, but the user's true need might still be broad:

- `"artificial intelligence"`
- `crime AND family`
- `"remote village"`
- `organized AND crime`
- `"human population"`

For these, strict structure can remove documents the qrels still consider weakly useful.

That is not automatically a bug. It is part of the lesson.

## Two adversarial examples to study

If you only inspect two examples after you finish M5, make them these:

### `"human world"`

Plain BM25 can rank a topically related document first because both words appear often enough.

Structured phrase search should promote the document that actually contains the phrase.

In the current movies audit:

- plain BM25 ranks `Monsters Inc.` first
- structured search promotes `Spirited Away`

That is a real top-rank correction, not just tail cleanup.

### `"family moves"`

This is another case where phrase structure changes the best answer.

In the current movies audit:

- plain BM25 ranks `Barfi` first
- structured search promotes `Inside Out`
- `Toy Story` remains as a weaker second match

This is exactly the kind of example that justifies the positional index.

## What students should notice

By the end of the audit, you should be able to say two things clearly:

1. M5 can fix wrong top-ranked answers when the query structure is genuinely important.
2. M5 can also overconstrain retrieval when the user's intent is broader than the syntax suggests.

That is the mature takeaway from the module.

## What done looks like

When M5 is complete, you should be able to:

1. Run boolean, phrase, and proximity queries
2. Explain why phrase/proximity require positions
3. Show that the existing M2 index is insufficient for those queries
4. Use a positional index extension without breaking M2-M4
5. Return ranked results using BM25 after structural filtering
6. Point to clear limitations that still require M6
7. Explain the difference between strict-intent and broad-topic structured queries
8. Use the audit split to justify when M5 helps and when it merely becomes stricter

If the module starts promising synonym handling, query expansion, or "semantic" behavior, it has drifted out of scope.

## Suggested test breakdown

Split tests by concept:

- parser tests
- boolean execution tests
- positional index tests
- phrase query tests
- proximity query tests
- ranked structured search tests
- CLI smoke tests

This matters because query parsing bugs and positional matching bugs are different classes of failure.

## Running tests

Proposed shape once the module lands:

```bash
pytest tests/test_query_parser.py -v
pytest tests/test_positional_index.py -v
pytest tests/test_query_executor.py -v
pytest tests/test_structured_search.py -v
```

## Python concepts used

- recursive descent or Pratt parsing
- dataclasses for query nodes
- set union / intersection / difference
- ordered position lists
- two-pointer style scans for phrase/proximity checks
- clean separation of parsing, retrieval, and ranking
