# M3 -> M4 Consequence Chain

Your BM25 parameter choices affect evaluation results in M4. This exercise asks you to predict those consequences before you see the numbers.

## Quick definitions

- **precision@k**: Of your top k results, how many are actually relevant? (0.0 to 1.0)
- **recall@k**: Of all relevant documents, how many appear in your top k results?
- **MRR (Mean Reciprocal Rank)**: How early does the first relevant result appear? Result #1 = MRR 1.0, result #5 = MRR 0.2.
- **nDCG (Normalized Discounted Cumulative Gain)**: Ranking quality score that rewards putting highly relevant results at the top. 1.0 = perfect ranking.

## How this works

For each scenario below, write your prediction BEFORE running the evaluation in M4. After M4, come back and compare.

## Scenario 1: Length normalization strength

**Default:** b = 0.75 (moderate length normalization)

Predict: What happens to precision@10 if you set b = 0.0 (no length normalization)?

Your prediction: ___

Reasoning: ___

**After M4:** Actual change: ___

## Scenario 2: Saturation control

**Default:** k1 = 1.2

Predict: What happens to nDCG if you set k1 = 0.1 (almost binary matching)?

Your prediction: ___

On this corpus (short product titles where tf is usually 1), will the effect be large or small? Why?

Your prediction: ___

**After M4:** Actual change: ___

## Scenario 3: Which parameter matters more?

On this 500-title corpus, which change moves nDCG further:
- Changing b from 0.0 to 0.75?
- Changing k1 from 0.2 to 2.0?

Your prediction: ___

Why: ___

**After M4:** Actual result: ___

## Scenario 4: Common term penalty

Query: "shoes for men" — "for" has very low (possibly negative) IDF.

Predict: Does including "for" in the query help or hurt ranking quality?

Your prediction: ___

What would happen if IDF was always positive (Lucene-style)?

Your prediction: ___

**After M4:** Actual comparison: ___

## Scenario 5: Single-term vs multi-term

Compare search quality for:
- Query A: "samsung" (1 term)
- Query B: "samsung galaxy" (2 terms)

Which has better precision@5? Why?

Your prediction: ___

**After M4:** Actual comparison: ___
