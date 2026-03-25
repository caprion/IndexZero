# M2 -> M4 Consequence Chain

Your index structure choices have consequences in M4 (Evaluation) and beyond. This exercise asks you to predict those consequences before you see them.

## Quick definitions

You haven't built M4 yet, so here's what these metrics mean:

- **precision@10**: Of your top 10 results, how many are actually relevant? (0.0 to 1.0)
- **MRR (Mean Reciprocal Rank)**: How early does the first relevant result appear? If it's result #1, MRR = 1.0. If it's result #5, MRR = 0.2.
- **nDCG (Normalized Discounted Cumulative Gain)**: A ranking quality score that rewards putting highly relevant results at the top. 1.0 = perfect ranking.
- **recall**: Of all relevant documents in the corpus, how many did your system return?
- **hapax legomenon**: A term that appears in exactly one document in the corpus. Often 40-50% of unique terms are hapax.

## How this works

1. Read each scenario below.
2. **Predict** what will happen. Write your prediction before running anything.
3. When you reach M4, **verify** by running the actual eval harness.
4. Compare your prediction to reality. The gap is where the learning lives.

## Scenario 1: Missing terms and retrieval completeness

**Setup:** Your index is built from 500 documents. A relevance-labeled query set has queries containing terms that appear in very few documents.

**Question:** The query is `"titanium water bottle"`. Suppose "titanium" appears in only 1 document, but that document is highly relevant.

- **Predict:** What happens to precision@10 if your index correctly returns this document? What if your index somehow misses it (e.g., due to a bug in posting list construction)?
- **Predict:** How would MRR (Mean Reciprocal Rank) change if the one relevant document moves from position 1 to position 10 in the results?

Your prediction:

_[Write your prediction here before reaching M4]_

Your verification (fill in at M4):

_[What actually happened]_

## Scenario 2: Document frequency and ranking discrimination

**Setup:** You compare two terms in a query: `"bluetooth earbuds"`.

"bluetooth" appears in 40 of 500 documents. "earbuds" appears in 8 of 500 documents.

**Question:** When BM25 (M3) uses your index to score documents:

- **Predict:** Which term contributes more to distinguishing relevant from irrelevant documents? Why?
- **Predict:** If your index has a bug where df("earbuds") = 40 instead of 8, how does that affect nDCG scores?

Your prediction:

_[Write your prediction here before reaching M4]_

Your verification (fill in at M4):

_[What actually happened]_

## Scenario 3: Document length normalization

**Setup:** Your index stores document_lengths for BM25 length normalization. Consider two documents:

- Doc A: "Boat Bluetooth Earbuds with Mic" (6 tokens)
- Doc B: "Boat Rockerz 450 Pro Plus ANC Bluetooth Wireless Over Ear Headphone with Mic 40mm Driver 70 Hours Playback" (18 tokens)

Both contain "bluetooth" once.

**Question:**

- **Predict:** Which document gets a higher BM25 score for the query "bluetooth"? Why?
- **Predict:** If your document_lengths are wrong (say, Doc B shows length 6 instead of 18), what happens to ranking quality?
- **Predict:** What nDCG impact would you expect from systematically wrong document lengths?

Your prediction:

_[Write your prediction here before reaching M4]_

Your verification (fill in at M4):

_[What actually happened]_

## Scenario 4: Posting list completeness

**Setup:** Your index is supposed to contain every term from every document. But suppose a bug causes your `build_index` to skip terms that appear exactly once in a document (hapax legomena).

**Question:** Hapax legomena often make up 40-50% of unique terms in a corpus.

- **Predict:** What fraction of query terms might fail to return any results?
- **Predict:** How would this affect recall? Precision? nDCG?
- **Predict:** Would the eval harness catch this bug, or would scores look "okay"?

Your prediction:

_[Write your prediction here before reaching M4]_

Your verification (fill in at M4):

_[What actually happened]_

## Reflection (fill in after M4 verification)

1. How many of your predictions were correct?
2. Which scenario surprised you most? What did you misunderstand about how index structure affects ranking?
3. Which of these failure modes is hardest to detect without an eval harness?
