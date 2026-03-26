# Eval

Evaluation metrics, benchmark fixtures, and hand-labeled relevance judgments for M4 and later modules.

## Contents

| File | Purpose |
|---|---|
| `qrels_template.csv` | Template for hand-labeling search results. Copy this, fill in relevance grades (0-3), and use it with the eval harness. |

## Relevance grades

| Grade | Label | Meaning |
|---|---|---|
| 0 | Irrelevant | The document has nothing to do with the query |
| 1 | Complement | Related but not what the user wants directly |
| 2 | Substitute | A reasonable alternative to the ideal result |
| 3 | Exact | Precisely what the user is looking for |

## Usage

```bash
# Run evaluation against the sample ESCI dataset
python -m indexzero eval --index index.json --qrels data/amazon_esci_sample/qrels.csv --queries data/amazon_esci_sample/queries.csv --k 10

# Run evaluation against your hand labels
python -m indexzero eval --index index.json --qrels eval/my_labels.csv --queries data/amazon_esci_sample/queries.csv --k 10
```

## ESCI format

The Amazon ESCI dataset uses letter labels (E/S/C/I) instead of numbers. The `load_qrels` function auto-detects this format and converts to numeric grades.

| ESCI | Grade | Meaning |
|---|---|---|
| E | 3 | Exact |
| S | 2 | Substitute |
| C | 1 | Complement |
| I | 0 | Irrelevant |
