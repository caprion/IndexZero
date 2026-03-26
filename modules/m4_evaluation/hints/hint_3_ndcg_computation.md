# Hint 3: nDCG Computation

## The formulas

```
DCG@k  = sum(i=1..k) rel_i / log2(i + 1)
IDCG@k = DCG of ideal ranking
nDCG@k = DCG@k / IDCG@k
```

## Step by step

### 1. Build a grade lookup

```python
grade_map = {j.doc_id: j.relevance for j in judgments}
```

### 2. Compute DCG for the actual ranking

```python
top_k = results.doc_ids[:k]
dcg = 0.0
for i, doc_id in enumerate(top_k):
    rel = grade_map.get(doc_id, 0)       # unjudged = 0
    dcg += rel / math.log2(i + 2)        # i+2 because i is 0-indexed, log2(1+1)=1.0
```

Why `i + 2`? Because `i` starts at 0, and we need `log2(rank + 1)` where rank starts at 1. So `log2(0 + 1 + 1) = log2(2) = 1.0` for the first position.

### 3. Compute IDCG (ideal ranking)

Sort ALL relevance grades from the judgments in descending order, take top k:

```python
all_grades = sorted([j.relevance for j in judgments], reverse=True)
ideal_top_k = all_grades[:k]
idcg = 0.0
for i, rel in enumerate(ideal_top_k):
    idcg += rel / math.log2(i + 2)
```

### 4. Normalize

```python
if idcg == 0.0:
    return 0.0
return dcg / idcg
```

## Worked example

Results: [d1, d2, d3], grades: d1=3, d2=0, d3=2, k=3

DCG:
- Position 1: 3 / log2(2) = 3 / 1.000 = 3.000
- Position 2: 0 / log2(3) = 0 / 1.585 = 0.000
- Position 3: 2 / log2(4) = 2 / 2.000 = 1.000
- DCG = 4.000

IDCG (ideal order: [3, 2, 0]):
- Position 1: 3 / log2(2) = 3 / 1.000 = 3.000
- Position 2: 2 / log2(3) = 2 / 1.585 = 1.262
- Position 3: 0 / log2(4) = 0 / 2.000 = 0.000
- IDCG = 4.262

nDCG = 4.000 / 4.262 = 0.939

## Common mistakes

- Using `math.log` (natural log) instead of `math.log2` (base 2)
- Off-by-one in the log denominator: `log2(i + 1)` instead of `log2(i + 2)` when i is 0-indexed
- Computing IDCG from the result list instead of from ALL judgments
- Using exponential gain `(2^rel - 1)` instead of linear gain (raw `rel`)
- Forgetting to handle IDCG = 0 (division by zero)
