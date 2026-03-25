# Data directory

## What's here

- **`flipkart_titles_tiny.csv`** — 8 fabricated product titles used in unit tests. These are deterministic and fast: every test run uses the same 8 rows. Format: `product_id,title`.

- **`flipkart_titles_500.csv`** — 500 synthetic Indian e-commerce product titles across 8 categories. Generated deterministically (`random.seed(42)`) by `scripts/generate_corpus.py` using only Python stdlib. Format: `product_id,title,category`.

  **Category distribution:**
  | Category | Count |
  |---|---|
  | Electronics | 100 |
  | Fashion | 80 |
  | Home & Kitchen | 80 |
  | Sports & Fitness | 60 |
  | Books & Education | 50 |
  | Beauty & Personal Care | 50 |
  | Grocery & Household | 40 |
  | Baby & Kids | 40 |

  Titles include tokenizer-challenging patterns: model numbers (`Redmi Note 13 Pro+ 5G`), units glued to digits (`750W`, `1.5L`, `28cm`), hyphens (`non-stick`, `3-in-1`), slashes (`8GB/256GB`, `Type-C/Lightning`), apostrophes (`L'Oreal`, `Haldiram's`), unusual brand casing (`boAt`, `iQOO`, `realme`), parenthetical specs (`(Pack of 3)`, `(Blue)`), pipe separators, and long compound titles.

  Regenerate with:
  ```
  .\.venv\Scripts\python.exe scripts\generate_corpus.py
  ```

## Dataset usage

- **Unit tests** use `flipkart_titles_tiny.csv` (8 rows, sub-second).
- **Exercises** (decision logs, break-its, Zipf analysis) use the 500-title dataset.
- **Evaluation** (M4+) will use ESCI relevance labels when that module ships.
