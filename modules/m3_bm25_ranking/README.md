# M3: BM25 Ranking

## You are here

```
M0  Ranking Audit          done — observation, no code
M1  Text Processing        done — tokenizer + vocabulary
M2  The Index              done — inverted index + lookup
>>> M3  Ranking             you are here
M4  Did It Work?           next — eval harness
M5  Smarter Queries        later — phrase, proximity
```

You built an index. You type "samsung phone" and get a list of documents. But which document should be first? Right now, `lookup` returns posting lists sorted by doc_id — alphabetical, meaningless. A user searching "samsung phone" wants the most relevant Samsung phone, not the one with the earliest product ID.

M3 turns an index into a search engine.

## Files to edit

| File | Action |
|---|---|
| `src/indexzero/scoring/scorer.py` | Implement 3 functions |
| `src/indexzero/scoring/contracts.py` | Read only (given) |

## The idea

BM25 scores each document by combining three signals:

**Rarity.** "samsung" appears in 20 of 500 documents. "for" appears in 400. Which term tells you more about what the user wants? IDF (Inverse Document Frequency) captures this — rare terms carry more weight.

**Repetition, with limits.** A product title mentioning "samsung" three times is probably more about Samsung than one mentioning it once. But ten times is not ten times better. BM25 saturates — diminishing returns on repetition.

**Length normalization.** "samsung" appearing once in a 5-word title is a stronger signal than "samsung" once in a 50-word title. BM25 adjusts for document length so short, focused documents are not disadvantaged.

The full formula:

```
score(term, doc) = IDF(term) * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avgdl))
```

You will implement this formula piece by piece.

## Glossary

| Term | Meaning |
|---|---|
| **tf** | Term frequency — how many times a term appears in one document |
| **df** | Document frequency — how many documents contain a term |
| **IDF** | Inverse Document Frequency: `ln((N - df + 0.5) / (df + 0.5))` |
| **dl** | Document length — token count for one document |
| **avgdl** | Average document length across the corpus |
| **k1** | Saturation parameter (default 1.2). Higher = repeated terms keep mattering longer |
| **b** | Length normalization parameter (default 0.75). 0 = ignore length, 1 = full normalization |
| **N** | Total number of documents in the corpus |
| **ln** | Natural logarithm (`math.log` in Python) |

## What you build

Three functions in `src/indexzero/scoring/scorer.py`:

| Function | Input | Output | Purpose |
|---|---|---|---|
| `compute_idf(term, index)` | A term + index | float | How rare is this term? |
| `score_bm25(term, doc_id, index, config)` | A term + document + index + params | float | Score one term in one document |
| `search(query_terms, index, config, top_k)` | Query terms + index + params | list of SearchResult | Ranked search results |

Two contracts in `contracts.py` (given, do not edit):
- `ScorerConfig(k1=1.2, b=0.75)` — tuning parameters
- `SearchResult(doc_id, score)` — a scored document

## Phase 0: Feel the pain

Before writing any M3 code, use your M2 index in a REPL:

```python
from indexzero.text_processing import TokenizerConfig, tokenize_document
from indexzero.indexing import build_index, lookup

config = TokenizerConfig()
docs = [
    tokenize_document("fk-001", "Samsung Galaxy M14 5G 128GB Blue", config),
    tokenize_document("fk-002", "Nike Running Shoes for Men", config),
    tokenize_document("fk-003", "Boat Bluetooth Earbuds with Mic", config),
    tokenize_document("fk-004", "Samsung Galaxy Tab S6 Lite WiFi", config),
]
index = build_index(docs)

# Search for "samsung" — which doc is best?
results = lookup(index, "samsung")
for p in results:
    print(f"  {p.doc_id}  tf={p.term_frequency}")
# Both docs have tf=1. No way to rank them. And 'for' matches too.
```

The index tells you WHERE terms appear. It does not tell you which documents are MOST relevant. That is what scoring does.

## Phase 0.5: Score by hand (worksheet)

Before implementing BM25, try scoring manually with this toy corpus:

| doc_id | text | tokens | length |
|---|---|---|---|
| d1 | "samsung phone" | samsung, phone | 2 |
| d2 | "phone case leather" | phone, case, leather | 3 |
| d3 | "case for phone" | case, for, phone | 3 |
| d4 | "for for for phone" | for(x3), phone | 4 |

Corpus stats: N=4, total_terms=12, avgdl=3.0

**Exercise 1:** Compute IDF for each term.

| term | df | IDF = ln((4 - df + 0.5) / (df + 0.5)) |
|---|---|---|
| samsung | 1 | ? |
| phone | 4 | ? |
| case | 2 | ? |
| for | 2 | ? |
| leather | 1 | ? |

You should get three different IDF regimes:
- **Positive IDF** — rare terms (samsung, leather). These help ranking.
- **Zero IDF** — terms in exactly half the corpus (case, for). These contribute nothing.
- **Negative IDF** — terms in most/all documents (phone). These are anti-informative.

If samsung's IDF is positive and phone's is negative, your formula is working.

**Exercise 2:** For query "samsung phone", which document should rank first?
- d1 has samsung(1) + phone(1), length 2 (short, focused)
- d2 has phone(1), length 3 (no samsung at all)

Samsung has positive IDF, so d1 gets a boost from it. Phone has negative IDF, so it penalizes every document equally. After implementing BM25, check whether the formula agrees with your intuition.

## Phase 1: Implement `compute_idf`

Implement the function in `scorer.py`. Run tests:

```bash
pytest tests/test_scorer.py::TestComputeIdf -v
```

Then explore in a REPL with the toy corpus above. Verify your hand computations match.

Try it on the 500-doc corpus too:
```python
# After building index from 500-doc CSV
idf_with = compute_idf("with", index)    # common term
idf_bluetooth = compute_idf("bluetooth", index)  # rare term
print(f"IDF 'with': {idf_with:.3f}")
print(f"IDF 'bluetooth': {idf_bluetooth:.3f}")
```

Note: negative IDF is expected for terms in more than half the corpus. Under this formula, very common terms are anti-informative — they reduce the score. Production systems sometimes shift the formula to avoid negatives. We keep it as-is because the negative case teaches something important about term discrimination.

## Phase 2: Implement `score_bm25`

This is the core formula. Use `compute_idf` inside it. Run tests:

```bash
pytest tests/test_scorer.py::TestScoreBm25 -v
```

Then experiment with parameters:

```python
from indexzero.scoring import ScorerConfig, score_bm25

# Compare a rare term across two different-length docs
# Samsung only appears in d1, but lets use 'leather' instead since it's also rare:
# Actually, use the 500-doc corpus where terms vary in document frequency.
# For the toy corpus, try 'samsung' in d1 vs compute the effect of b:

# With default b=0.75, length normalization matters
config = ScorerConfig()
# Try scoring a rare term in d1 (dl=2, short)
score_d1 = score_bm25("samsung", "d1", index, config)
print(f"samsung in d1 (dl=2): {score_d1:.4f}")
# Samsung has positive IDF, so this is a positive score.

# Now try phone — it is in ALL documents, negative IDF
score_phone_d1 = score_bm25("phone", "d1", index, config)
score_phone_d4 = score_bm25("phone", "d4", index, config)
print(f"phone in d1: {score_phone_d1:.4f}")
print(f"phone in d4: {score_phone_d4:.4f}")
# Both are negative. The shorter doc is LESS negative — which means
# for negative-IDF terms, the shorter doc is "less penalized."
# This reversal is important to understand.

# Turn off length normalization
score_b0 = score_bm25("samsung", "d1", index, ScorerConfig(b=0.0))
print(f"samsung b=0: {score_b0:.4f}")
# With b=0, document length has no effect.
```

## Phase 3: Implement `search`

Sum per-term scores across all documents, sort, return top-k. Run tests:

```bash
pytest tests/test_scorer.py::TestSearch -v
```

Then try a multi-term query:

```python
from indexzero.scoring import search, ScorerConfig

results = search(["samsung", "phone"], index, ScorerConfig())
for rank, r in enumerate(results, 1):
    print(f"  {rank}. {r.doc_id}  score={r.score:.4f}")
```

Look at the per-term breakdown:
```python
from indexzero.scoring import score_bm25, ScorerConfig

config = ScorerConfig()
for r in results:
    s_samsung = score_bm25("samsung", r.doc_id, index, config)
    s_phone = score_bm25("phone", r.doc_id, index, config)
    print(f"  {r.doc_id}: samsung={s_samsung:.3f} + phone={s_phone:.3f} = {r.score:.3f}")
```

BM25 is additive — each query term contributes independently. The total score is just the sum.

## Phase 4: Assessment

Complete the assessment artifacts in this module folder:
- `decision_log_template.md` — reflect on parameter choices and formula behavior
- `break_it_assignment.md` — introduce controlled bugs
- `consequence_chain.md` — predict how k1/b affect M4 evaluation metrics

## Optional Phase 5: CLI search

If you implemented save/load in M2, try the CLI:

```bash
python -m indexzero index --csv data/flipkart_titles_500.csv --output index.json
python -m indexzero search --index index.json --query "samsung phone" --top-k 5
python -m indexzero search --index index.json --query "bluetooth earbuds" --top-k 5
python -m indexzero search --index index.json --query "running shoes" --k1 0.5 --b 0.0
```

Note: the CLI normalizes your query by lowercasing and splitting on whitespace. This matches the default tokenizer. If you built your index with non-default settings (stemming, stopword removal), query terms may not match index terms exactly. This is a known limitation — M5 addresses query processing properly.

## What done looks like

When you finish M3, running `pytest tests/test_scorer.py -v` should show all tests passing. You should be able to:

1. Compute IDF for any term and explain why some are negative
2. Score any (term, document) pair with BM25 and predict how k1 and b affect the result
3. Run a multi-term search query and get ranked results
4. Use the CLI to search the 500-doc Flipkart corpus

## Running tests

```bash
# All M3 tests
pytest tests/test_scorer.py -v

# Just IDF tests
pytest tests/test_scorer.py::TestComputeIdf -v

# Just BM25 tests
pytest tests/test_scorer.py::TestScoreBm25 -v

# Just search tests
pytest tests/test_scorer.py::TestSearch -v
```

## Python concepts used

- `math.log` — natural logarithm
- `@dataclass(frozen=True)` — immutable config and result objects
- `defaultdict(float)` — accumulating scores per document
- `sorted()` with `key=` — multi-criteria sorting (score desc, doc_id asc for tie-breaking)
- Dictionary comprehension — building IDF lookup from postings
