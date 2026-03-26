# Hint 4: Orchestrating evaluate()

Open only if you are stuck on the `evaluate()` function.

## The pattern

`evaluate()` is not a new metric — it is the orchestrator. It ties together
all four metrics by running them once per query and averaging.

## Step 1: Group judgments by query

You receive a flat list of RelevanceJudgment objects across all queries.
Before computing anything, you need to split them into per-query buckets.

```
judgments_by_query = defaultdict(list)
for j in all_judgments:
    judgments_by_query[j.query_id].append(j)
```

## Step 2: For each QueryResults, look up the matching judgments

```
for qr in all_results:
    qj = judgments_by_query.get(qr.query_id, [])
    # call precision_at_k, recall_at_k, reciprocal_rank, ndcg_at_k
    # with (qr, qj, ...) and store in a QueryMetrics
```

If a query has no judgments, `qj` will be an empty list and the metrics
will return 0.0 for precision and nDCG, 1.0 for recall, 0.0 for RR.

## Step 3: Average across queries

Compute the mean of each metric across all per-query results.
Return an `EvalReport` with both per-query and mean values.
