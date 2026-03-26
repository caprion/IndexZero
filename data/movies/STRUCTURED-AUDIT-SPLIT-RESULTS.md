# Structured Audit Split Results

This note summarizes what happened after splitting the structured audit into:

- a **strict-intent** subset
- a **broad-topic** subset

## Why the split helps

The mixed profile was teaching two different lessons at once:

- sometimes structure is exactly the user's intent
- sometimes structure is stricter than the user's real information need

The split makes that distinction easier to explain.

## Strict-intent subset

Files:

- `structured_queries_strict.csv`
- `structured_qrels_strict.csv`

### Metric result

After adding two adversarial strict-intent cases, the strict subset now separates cleanly:

- plain BM25: `P@5 0.2333`, `R@5 1.0000`, `MRR 0.9167`, `nDCG@5 0.9425`
- structured search: `P@5 0.2333`, `R@5 1.0000`, `MRR 1.0000`, `nDCG@5 1.0000`

### What that really means

The reason the split works better now is that the new queries force a genuine top-rank decision.

The lists are also still much cleaner under M5. Examples:

- `"spirit world"`: plain BM25 returns `mov-023` plus four irrelevant tail results; structured search isolates `mov-023`
- `"space ranger"`: plain BM25 returns `mov-020` plus generic space films; structured search isolates `mov-020`
- `time NEAR/3 dilation`: plain BM25 returns `mov-009` plus unrelated time-themed results; structured search isolates `mov-009`
- `"human world"`: plain BM25 ranks `Monsters Inc.` first and `Spirited Away` second; structured phrase search correctly promotes `Spirited Away` to rank 1
- `"family moves"`: plain BM25 ranks `Barfi` first, while structured phrase search promotes `Inside Out` to rank 1 and keeps `Toy Story` as the weaker second match

So the strict subset still supports the student-facing lesson:

> M5 can both remove lexical noise and fix top-rank mistakes when the query intent is genuinely structural.

## Broad-topic subset

Files:

- `structured_queries_broad.csv`
- `structured_qrels_broad.csv`

### Metric result

At `k=5`:

- plain BM25: `P@5 0.3600`, `R@5 1.0000`, `MRR 1.0000`, `nDCG@5 0.9240`
- structured search: `P@5 0.3600`, `R@5 1.0000`, `MRR 1.0000`, `nDCG@5 0.8296`

### What that means

This subset reveals the tradeoff clearly.

For these queries, strict structure removes some lower-grade but still related documents:

- `crime AND family`
- `"remote village"`
- `organized AND crime`
- `"human population"`

That lowers graded gain under the current qrels, even though the structured lists are often easier to justify literally.

So the broad subset teaches the second student-facing lesson:

> Query syntax does not automatically equal user intent.

## Bottom line

The split was worth doing.

It gives two cleaner teaching modes:

1. **Strict-intent mode**: use M5 to show how phrase/boolean/proximity can clean up the tail of result lists.
2. **Broad-topic mode**: use M5 to discuss when literal structure may overconstrain retrieval.

## What to do next

The adversarial strict queries were the missing piece. They show students something stronger than "the tail got cleaner":

- plain lexical matching can be fooled by topical overlap
- phrase/proximity constraints can change the best-ranked answer

That is the clearest possible reason for M5 to exist.
