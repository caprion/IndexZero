# Structured Audit Results

This note summarizes what happened when the M5 structured-query path was run against the movies structured audit profile.

## What was compared

Two retrieval modes were compared on the same hand-labeled query set:

- plain lexical BM25 via `python -m indexzero search` / `eval`
- structured lexical retrieval via `python -m indexzero search-structured` / `eval-structured`

The query set lives in:

- `structured_queries.csv`
- `structured_qrels.csv`

The expanded profile currently contains 15 structured queries covering:

- exact phrase
- boolean `AND`
- proximity `NEAR/n`

## Main outcome

The aggregate evaluation metrics are still close, but the **result lists are meaningfully cleaner** under structured search for the targeted queries.

That is the real lesson from this audit.

The current profile is still sparse, so broad metrics do not fully reflect the benefit of stricter candidate filtering. But the query-by-query behavior does.

On the expanded profile at `k=5`:

- plain BM25: `P@5 0.2667`, `R@5 1.0000`, `MRR 1.0000`, `nDCG@5 0.9747`
- structured search: `P@5 0.2667`, `R@5 1.0000`, `MRR 1.0000`, `nDCG@5 0.9432`

That does **not** mean M5 failed. It means the audit now exposes a real tradeoff:

- structured search removes obvious lexical noise
- but strict phrase/boolean/proximity matching can also remove broader substitutes or complements

That is a good teaching outcome. M5 is not "always better." It is "more faithful to explicit structure."

## Query-by-query observations

### `smq-001` — `"artificial intelligence"`

Plain BM25 top results:

- `mov-073` Ex Machina
- `mov-069` 2001: A Space Odyssey
- `mov-007` The Matrix
- `mov-022` The Truman Show

Structured top results:

- `mov-073` Ex Machina
- `mov-069` 2001: A Space Odyssey
- `mov-007` The Matrix

What changed:

- the phrase filter removed a lexical false positive
- the surviving set is tighter without needing a new ranker

### `smq-002` — `crime AND family`

Plain BM25 top results:

- `mov-002` The Godfather
- `mov-016` The Departed
- `mov-024` Parasite
- `mov-125` Drishyam
- `mov-025` Get Out

Structured top results:

- `mov-002` The Godfather
- `mov-125` Drishyam

What changed:

- boolean filtering removed documents that were strong on one concept but weak or absent on the other
- this is the clearest example of M5 adding value

### `smq-003` — `"spirit world"`

Plain BM25 top results included unrelated lexical matches after the correct first hit.

Structured top results:

- `mov-023` Spirited Away

What changed:

- exact phrase search collapsed the candidate set to the intended film

### `smq-004` — `"police chief"`

Plain BM25 top results:

- `mov-125` Drishyam
- `mov-030` Jaws
- plus weaker lexical matches

Structured top results:

- `mov-125` Drishyam
- `mov-030` Jaws

What changed:

- phrase matching preserved the two relevant documents and removed noise

### `smq-005` — `mother NEAR/5 daughter`

Plain BM25 top results included the correct film first, but also several broader family-related documents.

Structured top results:

- `mov-093` Everything Everywhere All at Once

What changed:

- proximity matching turned a broad topical query into a relationship-sensitive query

### `smq-006` — `"space ranger"`

Plain BM25 top results:

- `mov-020` Toy Story
- then several generic space-related films

Structured top results:

- `mov-020` Toy Story

What changed:

- phrase matching removed generic term overlap and isolated the exact concept

### Additional phrase wins

The expanded profile added several more phrase queries with the same pattern:

- `"witness protection"` -> plain BM25 returned `mov-011` plus extra lexical matches; structured search isolated `mov-011`
- `"Day of the Dead"` -> plain BM25 returned `mov-029` plus several unrelated "day"/"dead" results; structured search isolated `mov-029`
- `"remote village"` -> plain BM25 returned `mov-107` plus broader rural/village results; structured search isolated `mov-107`
- `"human population"` -> plain BM25 returned `mov-007` plus broader human/society matches; structured search isolated `mov-007`
- `"luxury starship"` -> structured search isolated `mov-017`

These are good M5 cases because they are still lexical, but the phrase matters.

### Additional boolean and proximity wins

- `organized AND crime` -> plain BM25 returned broader crime-related films; structured search collapsed to `mov-011` and `mov-003`
- `alien AND invasion` -> structured search isolated `mov-037`
- `time NEAR/3 dilation` -> structured search isolated `mov-009`
- `great NEAR/2 shark` -> structured search isolated `mov-030`

These are the clearest examples of M5 adding structure without pretending to add semantics.

## The most important lesson from the denser labels

Once the qrels were expanded with more explicit false positives, a second lesson became visible:

- some structured queries are **strict-intent queries**
- some are **topic queries written with structured syntax**

For strict-intent cases, M5 is clearly better:

- `"spirit world"`
- `"space ranger"`
- `"witness protection"`
- `"Day of the Dead"`
- `time NEAR/3 dilation`

For ambiguous-intent cases, M5 may trade recall of weaker-but-related documents for cleaner precision:

- `crime AND family`
- `"remote village"`
- `organized AND crime`
- `"human population"`

That is exactly the kind of judgment students should learn to make:

> What did the user really mean when they wrote this query?

## Why nDCG dropped on the denser audit

The denser qrels exposed a subtle effect.

Example:

- for `organized AND crime`, plain BM25 returns the exact and substitute matches first, then a few complement-level crime films
- structured search keeps only the exact and substitute matches

If the qrels treat those broader crime films as low-grade complements rather than irrelevants, plain BM25 receives extra graded-gain credit in nDCG, even though its list is noisier.

So the lower structured nDCG here is not a bug by itself. It reflects the judgment file's view of query intent.

## What we learned about M5

This audit says M5 is doing the right kind of work:

- it is not trying to understand meaning
- it is making lexical search more precise when the query structure is explicit
- it improves candidate filtering more than it improves broad aggregate metrics
- it exposes the cost of strict matching when the user intent is broader than the syntax suggests

That is exactly the right role for M5.

## What we learned about the CLI

There is an important behavioral difference between the plain and structured commands:

- `search` is still a simple whitespace-based BM25 query path
- `search-structured` understands quotes, boolean operators, and `NEAR/n`

Example:

- `search --query '"artificial intelligence"'` does not behave like phrase search
- `search-structured --query '"artificial intelligence"'` does

This is good for now because it keeps M5 explicit. But later we may want a single unified search entry point with optional structured parsing.

## Current weaknesses

The audit also surfaced a few limits:

1. The structured profile is still very small, so the metrics are more illustrative than definitive.
2. Sparse qrels mean precision@k is sensitive to missing judgments.
3. Boolean queries are intentionally strict, so some apparently relevant topical documents disappear if they miss one required term.
4. The plain `search` CLI does not share the structured parsing behavior of `search-structured`.
5. Some query judgments now mix strict-intent and broad-topic interpretations, which is educationally useful but reduces metric clarity.

## Recommended next moves

1. Split the structured audit into two labeled subsets:
   - strict-intent queries
   - broader topical queries with structured syntax
2. For strict-intent queries, keep complements mostly out of the qrels so phrase/proximity gains show up cleanly.
3. For broader topical queries, keep the current mixed labels and use them to discuss precision/recall tradeoffs.
4. Consider a unified search entry point later, but only after M5's explicit mode has taught the concept cleanly.
5. Keep M5 lexical. Do not add synonym expansion or semantic fallback here.

## Bottom line

The audit result is simple:

M5 is already useful when the query deliberately expresses structure.

It narrows candidate sets, removes obvious lexical noise, and makes phrase/proximity behavior visible without stepping on M6's role.
