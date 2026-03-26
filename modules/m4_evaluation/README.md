# M4: Did It Work?

## You are here

```
M0  Ranking Audit          done — observation, no code
M1  Text Processing        done — tokenizer + vocabulary
M2  The Index              done — inverted index + lookup
M3  Ranking                done — BM25 scorer
>>> M4  Did It Work?       you are here
M5  Smarter Queries        next — phrase, proximity
M6  Meaning, Not Words     later — vector retrieval
```

You built a search engine. Type "samsung phone" and get ranked results. But are the results good? Better than random? Better than alphabetical? You need a number.

M4 builds an evaluation harness — the tool that tells you whether your search engine is actually working.

## Files to edit

| File | Action |
|---|---|
| `src/indexzero/evaluation/metrics.py` | Implement 5 functions |
| `src/indexzero/evaluation/contracts.py` | Read only (given) |
| `src/indexzero/evaluation/qrels_io.py` | Read only (given) |

## The idea

Search quality is measured by comparing your engine's ranked output against human relevance judgments ("qrels"). Each judgment says: "for query X, document Y has relevance grade Z."

Four metrics capture different aspects of quality:

**Precision@k** — of the top-k results you returned, how many are actually relevant? Measures whether the user sees junk on the first page.

**Recall@k** — of all the relevant documents that exist, how many did you find in your top-k? Measures whether you are missing good results.

**Reciprocal Rank (RR)** — how far down must the user scroll to find the first useful result? 1/1 if it is first, 1/3 if third, 0 if never. When averaged across queries, this becomes MRR (Mean Reciprocal Rank).

**nDCG@k** — a position-aware score that gives more credit for placing highly relevant docs at the top. Unlike precision (binary: relevant or not), nDCG uses the full graded scale (Exact > Substitute > Complement > Irrelevant).

## Glossary

| Term | Meaning |
|---|---|
| **qrels** | Query relevance judgments — human labels saying how relevant each document is for each query |
| **P@k** | Precision at cutoff k |
| **R@k** | Recall at cutoff k |
| **MRR** | Mean Reciprocal Rank — average of 1/rank-of-first-relevant across queries |
| **DCG** | Discounted Cumulative Gain — sum of relevance grades weighted by log position |
| **IDCG** | Ideal DCG — DCG of the perfect ranking |
| **nDCG** | Normalized DCG — DCG / IDCG, always in [0, 1] |
| **ESCI** | Exact / Substitute / Complement / Irrelevant — the grading scale |

## What you build

Five functions in `src/indexzero/evaluation/metrics.py`:

| Function | Input | Output | Purpose |
|---|---|---|---|
| `precision_at_k(results, judgments, k)` | Ranked list + qrels | float | What fraction of top-k is relevant? |
| `recall_at_k(results, judgments, k)` | Ranked list + qrels | float | What fraction of all relevant did we find? |
| `reciprocal_rank(results, judgments)` | Ranked list + qrels | float | How far to first relevant? |
| `ndcg_at_k(results, judgments, k)` | Ranked list + qrels | float | Position-weighted graded score |
| `evaluate(all_results, all_judgments, k)` | Multiple queries | EvalReport | Full evaluation across queries |

Four contracts in `contracts.py` (given, do not edit):
- `RelevanceJudgment(query_id, doc_id, relevance)` — one human label
- `QueryResults(query_id, doc_ids)` — ranked result list
- `QueryMetrics(query_id, precision_at_k, recall_at_k, reciprocal_rank, ndcg_at_k)` — per-query scores
- `EvalReport(per_query, mean_*, k, num_queries)` — aggregate report

## Phase 0: Which is better?

Before writing any M4 code, look at these two search results for "wireless earbuds":

**Config A** (k1=1.2, b=0.75):
```
1. Wireless Bluetooth Earbuds with Charging Case
2. boAt Airdopes 141 TWS Earbuds with 42H Playtime
3. Noise Buds VS104 Bluetooth Truly Wireless Earbuds
4. Sony WH-1000XM5 Wireless Noise Cancelling Headphones
5. boAt Stone 180 Portable Bluetooth Speaker 5W
```

**Config B** (k1=0.1, b=0.0):
```
1. Noise Buds VS104 Bluetooth Truly Wireless Earbuds
2. Sony WH-1000XM5 Wireless Noise Cancelling Headphones
3. Wireless Bluetooth Earbuds with Charging Case
4. boAt Airdopes 141 TWS Earbuds with 42H Playtime
5. boAt Stone 180 Portable Bluetooth Speaker 5W
```

Which is better? You might have an opinion. But "I think A looks better" is not a number. You cannot tune 50 queries by reading all the results. You need a metric.

That is what this module builds.

## Phase 0.5: Hand-label worksheet

Before implementing metrics, build intuition by hand-labeling search results.

1. Pick 5 queries from the 500-product corpus (or use the ESCI sample queries).
2. Run your BM25 search from M3: `python -m indexzero search --index index.json --query "your query" --top-k 10`
3. For each result, assign a relevance grade:
   - **3 (Exact)** — this is exactly what the user wants
   - **2 (Substitute)** — a reasonable alternative
   - **1 (Complement)** — related but not the main thing
   - **0 (Irrelevant)** — nothing to do with the query
4. Save your labels in `eval/qrels_template.csv`

This is tedious. That is the point. Evaluation requires human effort. The metrics you build next automate the math, but someone still has to decide what "relevant" means.

## Phase 1: Precision@k and Recall@k

### Precision@k

The simplest metric: what fraction of your top-k results are relevant?

```
P@k = |{relevant docs in top k}| / k
```

A document is "relevant" if its grade >= the threshold (default 2, meaning Substitute or Exact). Unjudged documents get grade 0.

**Example:** Top-5 results: [Exact, Irrelevant, Substitute, Complement, Irrelevant]
- At threshold=2: 2 relevant out of 5 -> P@5 = 0.4
- At threshold=1: 3 relevant out of 5 -> P@5 = 0.6

Important: divide by k, not by the number of results returned. If you only have 3 results but k=10, that is P@10 = 2/10, not 2/3.

### Recall@k

How many of all the relevant documents did you find?

```
R@k = |{relevant in top k}| / |{all relevant in qrels}|
```

If there are 10 relevant documents in the qrels but only 3 in your top-5, R@5 = 3/10 = 0.3.

Edge case: if there are zero relevant documents in the qrels, return 1.0. You cannot miss what does not exist.

Implement both, then run:

```bash
pytest tests/test_metrics.py::TestPrecisionAtK -v
pytest tests/test_metrics.py::TestRecallAtK -v
```

## Phase 2: Reciprocal Rank (MRR)

How far down does the user have to scroll to find the first relevant result?

```
RR = 1 / rank_of_first_relevant
```

Rank is 1-indexed: the first result has rank 1. If no relevant result exists, RR = 0.

When averaged across queries, this becomes Mean Reciprocal Rank (MRR):
```
MRR = (1/|Q|) * sum(1 / rank_i for each query)
```

**Example:**
- Query 1: first relevant at position 1 -> RR = 1.0
- Query 2: first relevant at position 3 -> RR = 0.333
- Query 3: no relevant found -> RR = 0.0
- MRR = (1.0 + 0.333 + 0.0) / 3 = 0.444

Only the first relevant result matters. Having ten relevant results at positions 2-11 gives the same RR as one relevant result at position 2.

Implement and run:

```bash
pytest tests/test_metrics.py::TestReciprocalRank -v
```

## Phase 3: nDCG@k

Precision treats all relevant docs the same. nDCG (Normalized Discounted Cumulative Gain) does not — it rewards placing highly relevant documents at higher ranks.

### Step 1: DCG (Discounted Cumulative Gain)

```
DCG@k = sum(i=1..k) rel_i / log2(i + 1)
```

Each position contributes its relevance grade, discounted by log of the position. Position 1 gets a discount of 1/log2(2) = 1.0, position 2 gets 1/log2(3) = 0.63, position 3 gets 1/log2(4) = 0.50.

### Step 2: IDCG (Ideal DCG)

What would DCG be if you had the perfect ranking? Sort ALL relevance grades from the qrels in descending order and compute DCG on that ideal list.

### Step 3: Normalize

```
nDCG@k = DCG@k / IDCG@k
```

If IDCG is 0 (no relevant docs), return 0.0.

### Worked example

Results: [d1, d2, d3], grades from qrels: d1=3, d2=0, d3=2

| Position i | doc | rel_i | log2(i+1) | rel_i / log2(i+1) |
|---|---|---|---|---|
| 1 | d1 | 3 | 1.000 | 3.000 |
| 2 | d2 | 0 | 1.585 | 0.000 |
| 3 | d3 | 2 | 2.000 | 1.000 |

**DCG@3 = 3.000 + 0.000 + 1.000 = 4.000**

Ideal ranking (sort grades desc): [3, 2, 0]

| Position i | rel_i | log2(i+1) | rel_i / log2(i+1) |
|---|---|---|---|
| 1 | 3 | 1.000 | 3.000 |
| 2 | 2 | 1.585 | 1.262 |
| 3 | 0 | 2.000 | 0.000 |

**IDCG@3 = 3.000 + 1.262 + 0.000 = 4.262**

**nDCG@3 = 4.000 / 4.262 = 0.939**

The ranking is 93.9% of ideal. The only mistake was placing d2 (irrelevant) at position 2 instead of d3 (grade 2).

Note: we use LINEAR gain (raw relevance grade). Some systems use exponential gain (2^rel - 1). We keep it linear for clarity.

Implement and run:

```bash
pytest tests/test_metrics.py::TestNdcgAtK -v
```

## Phase 4: evaluate() orchestrator

Wire the four metrics together. The `evaluate` function:

1. Groups all judgments by query_id
2. For each QueryResults, computes all four metrics
3. Averages across all queries
4. Returns an EvalReport

```bash
pytest tests/test_metrics.py::TestEvaluate -v
```

Then try it on the ESCI sample data using the CLI:

```bash
python -m indexzero index --csv data/amazon_esci_sample/products.csv --output esci_index.json --doc-id-column product_id
python -m indexzero eval --index esci_index.json --qrels data/amazon_esci_sample/qrels.csv --queries data/amazon_esci_sample/queries.csv --k 10
```

## Phase 5: Experiments

Now that you have metrics, run experiments:

### Tokenizer config sweep

Build indexes with different tokenizer settings and compare metrics:

| Config | Settings | P@10 | nDCG@10 |
|---|---|---|---|
| Baseline | defaults | ? | ? |
| No lowercase | --no-lowercase | ? | ? |
| With stopwords | --drop-stopwords | ? | ? |
| With stemming | --stemming suffix | ? | ? |

Which tokenizer config gives the best nDCG? Does it also have the best precision?

### BM25 parameter sweep

Same index, different k1/b:

| k1 | b | P@10 | nDCG@10 | MRR |
|---|---|---|---|---|
| 1.2 | 0.75 | ? | ? | ? |
| 0.5 | 0.75 | ? | ? | ? |
| 1.2 | 0.0 | ? | ? | ? |
| 2.0 | 0.75 | ? | ? | ? |

### Consequence chain audit

Look back at your M3 consequence chain predictions. Were they correct? Which parameter had the bigger effect on nDCG — k1 or b? Why?

## What done looks like

When you finish M4, running `pytest tests/test_metrics.py -v` should show all tests passing. You should be able to:

1. Compute precision, recall, MRR, and nDCG for any ranked result list
2. Explain why nDCG rewards placing high-grade docs at the top
3. Run evaluation across multiple queries and interpret the report
4. Use the eval CLI to compare different search configurations

## Running tests

```bash
# All M4 tests
pytest tests/test_metrics.py -v

# Just precision tests
pytest tests/test_metrics.py::TestPrecisionAtK -v

# Just recall tests
pytest tests/test_metrics.py::TestRecallAtK -v

# Just reciprocal rank tests
pytest tests/test_metrics.py::TestReciprocalRank -v

# Just nDCG tests
pytest tests/test_metrics.py::TestNdcgAtK -v

# Just evaluate tests
pytest tests/test_metrics.py::TestEvaluate -v
```

## Python concepts used

- `math.log2` — base-2 logarithm (for nDCG discount factor)
- `collections.defaultdict` — grouping judgments by query_id
- List slicing (`[:k]`) — cutting results to top-k
- Set operations — fast membership testing for relevant doc lookup
- `sorted()` with `reverse=True` — descending sort for ideal ranking
