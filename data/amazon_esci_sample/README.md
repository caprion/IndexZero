# Amazon ESCI Sample

40 products, 20 queries, and 100 relevance judgments in ESCI format.
Used by M4 exercises and the CLI `eval` command.

## Files

- **products.csv** — `product_id`, `product_title` (40 rows)
- **queries.csv** — `query_id`, `query` (20 rows)
- **qrels.csv** — `query_id`, `product_id`, `esci_label` (E/S/C/I letters)

The eval harness auto-converts ESCI letters to numeric grades:
E=3 (Exact), S=2 (Substitute), C=1 (Complement), I=0 (Irrelevant).
