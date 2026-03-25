# M2 Break-It Assignment

You built an inverted index that passes all tests. Now break it on purpose. Each task asks you to introduce a specific bug, observe what happens, then fix it.

## Rules

- Introduce ONE bug at a time.
- Run the tests after each bug. Note which tests catch it and which don't.
- Fix the bug before introducing the next one.

## Task 1: Duplicate postings

**Bug:** In `build_index`, append a Posting to the list for every token occurrence instead of aggregating per-document.

For the text "RAM 8GB RAM 16GB RAM 32GB", the term "ram" should have ONE posting with tf=3. Make it create THREE postings with tf=1.

**Observe:**
- Which test catches this?
- What would happen to BM25 scores if df(term) = 3 instead of 1 for a single document?

**Your notes:**

_[What happened]_

## Task 2: Wrong document lengths

**Bug:** Set all document_lengths to the same value (e.g., 10) regardless of actual token count.

**Observe:**
- Which tests catch this?
- When BM25 uses these lengths for normalization, what ranking errors would result?
- Would short documents be over-scored or under-scored?

**Your notes:**

_[What happened]_

## Task 3: Missing a term

**Bug:** In `build_index`, skip any term that appears in more than 3 documents (high-df terms).

**Observe:**
- How many terms disappear from the index?
- Which test catches this?
- Is it possible for a query to return zero results because of this?

**Your notes:**

_[What happened]_

## Task 4: Unsorted posting lists

**Bug:** Remove the sort-by-doc_id step from your posting lists. Use insertion order instead.

**Observe:**
- Which test catches this?
- Does the index still work for lookup?
- What would break if a future module (M8) tried to merge two indexes by doing a sorted merge on posting lists?

**Your notes:**

_[What happened]_

## Task 5: Zero-frequency posting

**Bug:** For one term, append a Posting with `term_frequency=0`.

**Observe:**
- Which test catches this?
- What would BM25 compute for a term with tf=0? (Hint: the numerator of the BM25 tf component becomes 0.)
- Is a zero-frequency posting ever valid?

**Your notes:**

_[What happened]_

## Reflection

1. Which bug was hardest to detect just by looking at the output?
2. Which bug would cause the most damage to search quality?
3. Are there failure modes your tests DON'T catch? What additional test would you write?
