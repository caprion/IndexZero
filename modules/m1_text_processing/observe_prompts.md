# M1 Instrument-and-Observe Prompts

Add measurements to your pipeline, run on the corpus, report numbers, interpret them.

The numbers come from YOUR pipeline with YOUR config choices. Interpretation requires connecting those numbers to your design decisions.

## Setup

Make sure your tokenizer and vocabulary builder work on the tiny dataset:

```bash
python -m indexzero vocab --csv data/flipkart_titles_tiny.csv
```

For richer observations, a larger dataset will be available in future modules. For now, work with the tiny dataset — 8 rows is enough to see the patterns.

## Observation 1: Vocabulary size across configs

Run your vocabulary builder with three different configs using CLI flags:

```bash
python -m indexzero vocab --csv data/flipkart_titles_tiny.csv
python -m indexzero vocab --csv data/flipkart_titles_tiny.csv --drop-stopwords
python -m indexzero vocab --csv data/flipkart_titles_tiny.csv --drop-stopwords --stemming suffix
```

Record the vocabulary size from each run:

| Config | Vocab size | Total terms | Ratio (vocab/terms) |
|---|---|---|---|
| Default (lowercase only) | | | |
| + stopword removal | | | |
| + stopword removal + stemming | | | |

**Interpret:**
- By what percentage did stopword removal shrink the vocabulary?
- By what percentage did stemming further shrink it?
- Which had a bigger effect? Is that what you expected?

## Observation 2: Term frequency distribution

Pick the most common 10 tokens in your vocabulary (by collection frequency).

| Rank | Token | Collection frequency | Document frequency |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |
| 6 | | | |
| 7 | | | |
| 8 | | | |
| 9 | | | |
| 10 | | | |

**Interpret:**
- Are the top terms useful for distinguishing between documents, or are they noise?
- How many of them are stopwords (even if you didn't remove stopwords)?
- Would a searcher ever use these terms as a query? What does that tell you?

## Observation 3: Tokens per document

Record the token count for each of the 8 documents:

| doc_id | Raw title | Token count |
|---|---|---|
| fk-001 | | |
| fk-002 | | |
| fk-003 | | |
| fk-004 | | |
| fk-005 | | |
| fk-006 | | |
| fk-007 | | |
| fk-008 | | |

**Interpret:**
- What's the average document length? What's the range?
- In M3, BM25 uses document length for normalization. Documents much shorter or longer than average get scored differently. Which documents in your corpus will be most affected?

## Observation 4: Zipf's law check

Zipf's law says that in a large corpus, the most common word appears roughly twice as often as the second most common, three times as often as the third, and so on. The nth most common token has frequency proportional to 1/n.

Use the 500-title dataset for this observation (the 8-row tiny set is too small for frequency distributions):

```bash
python -m indexzero vocab --csv data/flipkart_titles_500.csv
```

List the top 50 tokens by frequency.

**Interpret:**
- Does the distribution roughly follow Zipf's law (the nth most common token has frequency ∝ 1/n)?
- At what rank does the frequency drop to 1 (hapax legomena — tokens that appear only once in the corpus)?
- What fraction of your vocabulary appears in only one document?

## Observation 5: The "HP" problem

Run:
```bash
python -m indexzero tokenize --text "HP 15s Ryzen 5 Laptop"
python -m indexzero tokenize --text "hp motor 750W mixer grinder"
```

**Interpret:**
- Do these produce overlapping tokens?
- If a user searches for "HP laptop", would your tokenizer cause the mixer grinder to match?
- Is this a problem worth solving at the tokenizer level, or should ranking (M3) handle it?

## Reflection

1. Which observation taught you something you didn't expect?
2. If you had to present one number to justify your tokenizer config to a colleague, which number would you pick and why?
3. What measurement would you add that isn't listed here?
