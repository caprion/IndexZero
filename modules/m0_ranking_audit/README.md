# M0 - The Problem

M0 stays no-code on purpose. Students inspect a live e-commerce search experience, notice what the ranking is doing, and make hypotheses before the course hands them formal tools.

Keep the core idea simple: this is still the **Ranking Audit**. We are refining the worksheet around it, not replacing it.

## What students should leave with

- Search is ranking under constraints, not database lookup.
- A result page gives clues about the system, not a full explanation.
- "Good ranking" depends on what the system is trying to optimize.
- Early hypotheses are useful even when they are incomplete.

## Quick framing: IR vs search APIs vs vector search vs RAG

Students do not need a theory lecture here. They do need enough vocabulary to stop collapsing everything into "AI search."

- **Information retrieval (IR)** is the broader problem: take an information need and return useful items in a useful order.
- A **search API** is the surface a product exposes to retrieve results.
- **Vector search** is one retrieval method. It can help with meaning-heavy matches, but it is not the whole search system.
- **RAG** is an application pattern that uses retrieval to ground generation. It depends on search; it does not replace it.

M0 names these lightly, then moves back to observation.

## Exercise

Pick one Indian e-commerce site and run three search types:

- one broad query
- one specific query
- one ambiguous query

Then complete the ranking audit worksheet:

1. Capture the top three results for each query.
2. Write a concrete hypothesis for why each result ranked where it did.
3. Point to evidence you can actually see on the page: title match, brand match, price, discount badge, sponsored label, ratings, review count, delivery promise, category fit, and so on.
4. Name at least one alternative explanation when more than one signal could explain the ranking.
5. Mark where you are unsure instead of pretending you know.
6. Identify one surprising result and give your best explanation for what the system may have optimized incorrectly.
7. Do one comparison exercise showing how the "best" ranking changes when the system goal changes.

## Deliverable

Make a copy of `hypothesis_template.md` and submit your filled-in Ranking Audit worksheet with your own filename.

Use `rubric.md` to see what good work looks like. The rubric is a self-check and assessment aid, not a separate student submission. This is still **not graded for correctness**. It is graded, lightly, for the quality of reasoning:

- specificity
- evidence
- alternatives
- uncertainty

This becomes the baseline artifact students revisit at M9.

## Comparison exercise

Use one query from your worksheet and compare two possible system goals:

- **Goal A:** help the user buy fast with high confidence
- **Goal B:** help the user explore options or discover alternatives

Explain what should rank first in each case, what signals should matter more, and what should move down. This is the simplest way to make students feel that ranking depends on product goals, not just "accuracy."

## Light foreshadowing for later modules

Later in the course, students will learn to make explicit **relevance judgments** and test systems against benchmarks. M0 does not turn into an evaluation module. It just plants one idea early:

> somebody eventually has to decide what "good result" means, and that decision is never context-free.

The quick labels in the worksheet stay intentionally simple here. Later modules will replace them with more formal relevance language and evaluation logic.

## Connection to M1

M0 starts with visible ranking clues. M1 explains why some of those clues exist in the first place by forcing students to think about how text gets normalized, tokenized, and matched.

## Why this matters

- It makes students feel that search is ranking, not lookup.
- It surfaces naive assumptions before later modules have to break them.
- It introduces just enough vocabulary to separate IR, APIs, vector retrieval, and RAG.
- It gives the later modules a clean narrative thread to return to.
