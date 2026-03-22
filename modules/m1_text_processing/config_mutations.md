# M1 Config Mutation Tests

Change one config flag. Predict which tests fail and why. Then run and compare.

## How this works

1. Start with all tests passing under your current config.
2. For each mutation below, **predict** what happens before running pytest.
3. Run the CLI with the mutation flag to see the output, then run pytest to compare.
4. The point is not to be right — it's to build an accurate mental model.

> **How to read a pytest failure:** Look at the LAST line of each failure — that's the assertion that broke (e.g., `assert token == token.lower()`). Then look one line above for the actual values your code produced. The test name tells you which rule (invariant) was violated. Ignore the rest of the traceback for now.

**Using config flags from the CLI:**

```bash
# Default config (lowercase on, everything else off):
python -m indexzero tokenize --text "Nike Revolution Running Shoes for Men"

# Disable lowercasing:
python -m indexzero tokenize --text "Nike Revolution Running Shoes for Men" --no-lowercase

# Compare vocab size across configs:
python -m indexzero vocab --csv data/flipkart_titles_tiny.csv
python -m indexzero vocab --csv data/flipkart_titles_tiny.csv --drop-stopwords
python -m indexzero vocab --csv data/flipkart_titles_tiny.csv --drop-stopwords --stemming suffix
```

## Mutation 1: Disable lowercasing

**Change:** Run with `--no-lowercase`:

```bash
python -m indexzero tokenize --text "HP 15s Ryzen 5 Laptop" --no-lowercase
python -m indexzero vocab --csv data/flipkart_titles_tiny.csv --no-lowercase
```

**Predict before running:**

- Which test(s) will fail? List them by name.
- Why will they fail? What invariant breaks?
- What will the actual output look like?

Your prediction:

_[Write before running]_

**Run:** `pytest tests/test_tokenizer.py -v`

> Note: The tests create their own configs via fixtures, so your CLI flags don't apply to pytest. The prediction exercise is: "If the test's default config had this flag, which tests would break?" Use the CLI output to understand the *behavior*, then predict the *test impact*.

What actually happened:

_[Write after running]_

## Mutation 2: Enable stopword removal

**Change:** Run with `--drop-stopwords`:

```bash
python -m indexzero tokenize --text "Nike Revolution Running Shoes for Men" --drop-stopwords
python -m indexzero vocab --csv data/flipkart_titles_tiny.csv --drop-stopwords
```

**Predict before running:**

- Will the tokenizer produce more or fewer tokens?
- Which specific test(s) might fail or change behavior?
- Will any vocabulary test break? Why or why not?

Your prediction:

_[Write before running]_

**Run:** `pytest tests/ -v`

What actually happened:

_[Write after running]_

## Mutation 3: Enable stemming

**Change:** Run with `--stemming suffix`:

```bash
python -m indexzero tokenize --text "Nike Revolution Running Shoes for Men" --stemming suffix
python -m indexzero vocab --csv data/flipkart_titles_tiny.csv --stemming suffix
```

**Predict before running:**

- How will the vocabulary size change? More tokens, fewer, or the same?
- Which tests check token equality that might now break?
- Will `token_count == sum(term_counts.values())` still hold? Why?

Your prediction:

_[Write before running]_

**Run:** `pytest tests/ -v`

What actually happened:

_[Write after running]_

## Mutation 4: Enable numeric boundary splitting

**Change:** Run with `--split-numeric`:

```bash
python -m indexzero tokenize --text "HP 15s Ryzen 5 Laptop 16GB RAM 512GB SSD" --split-numeric
python -m indexzero vocab --csv data/flipkart_titles_tiny.csv --split-numeric
```

**Predict before running:**

- How does `"8GB"` change? What about `"Note13"` or `"512GB"`?
- Will this increase or decrease the total token count?
- Will any term_count invariant break?

Your prediction:

_[Write before running]_

**Run:** `pytest tests/ -v`

What actually happened:

_[Write after running]_

## Mutation 5: Two changes at once

**Change:** Run with `--drop-stopwords --stemming suffix`:

```bash
python -m indexzero tokenize --text "Nike Revolution Running Shoes for Men" --drop-stopwords --stemming suffix
python -m indexzero vocab --csv data/flipkart_titles_tiny.csv --drop-stopwords --stemming suffix
```

**Predict before running:**

- How does the combined effect differ from each change alone?
- Will vocabulary size shrink more than the sum of individual shrinks?
- Is there any interaction between these two flags?

Your prediction:

_[Write before running]_

**Run:** `pytest tests/ -v`

What actually happened:

_[Write after running]_

## Reflection

1. Which mutation surprised you the most?
2. Can you rank the four flags by how much they change the output? (most impact → least)
3. If you had to pick a "safe default" config for an unknown corpus, what would it be and why?
