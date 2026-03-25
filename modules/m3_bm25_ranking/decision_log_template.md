# M3 Decision Log

Record your thinking about BM25 behavior. These are not graded — they are for your own reference when you compare results in M4.

## Decision 1: Parameter defaults

k1 = 1.2, b = 0.75 are the "textbook" defaults. But this corpus is not a textbook corpus — it is 500 short product titles.

**Question:** Do the defaults make sense for short product titles? Or would different values work better?

Your thinking: ___

What would you change (if anything) and why: ___

## Decision 2: Negative IDF behavior

Under the standard formula, terms in more than half the corpus get negative IDF. This means a very common query term can reduce a document's total score.

**Question:** Is this the right behavior for product search? Should "for" in "shoes for men" penalize documents?

Your thinking: ___

Alternative approaches you considered: ___

## Decision 3: Score interpretation

BM25 scores are not probabilities. They are unbounded, can be negative, and only meaningful relative to other scores for the same query.

**Question:** A document scores 3.2 for query A and 1.1 for query B. Does that mean query A is a "better match"? Why or why not?

Your answer: ___

## Decision 4: Tie-breaking

When two documents have the same BM25 score, your implementation breaks ties by doc_id (alphabetical).

**Question:** Is alphabetical doc_id a good tie-breaker for a real search engine? What might be better?

Your ideas: ___

## Decision 5: Duplicate query terms

If a user searches "samsung samsung phone", should "samsung" count twice in the score?

Your implementation does: ___

Your reasoning: ___

What a production search engine might do: ___

## Decision 6: IDF as the dominant signal

On this corpus, most terms have tf=1 (product titles are short). That means BM25 often reduces to approximately IDF-weighted binary matching — a term is either in the document or it is not, and the IDF decides how much that matters.

**Question:** When does tf actually make a difference on short-text corpora? Can you find an example in the 500-doc dataset where tf > 1 changes the ranking?

Your finding: ___
