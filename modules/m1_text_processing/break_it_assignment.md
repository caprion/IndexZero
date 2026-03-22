# M1 Break-It Assignment

Take your working tokenizer and break it with concrete examples.

## Goal

Show that a tokenizer which "works on normal text" can still be wrong for search. Every failure you find makes your understanding deeper than the code itself.

## Instructions

For each category below:

1. Provide one concrete input string.
2. Show the actual output from YOUR tokenizer (copy-paste from terminal).
3. Show what the output SHOULD be for good retrieval.
4. Explain why the difference matters for search results.

Use the CLI:
```bash
python -m indexzero tokenize --text "your input here"
```

## Attack categories

### 1. Punctuation glue

Find a product title where punctuation joins two words that should be separate tokens. Show what your tokenizer does with it.

Your input:
Your output:
Better output:
Why it matters:

### 2. Case duplicates

Find a case where your tokenizer creates duplicate meanings because of uppercase/lowercase differences. (Hint: think about brands.)

Your input:
Your output:
Better output:
Why it matters:

### 3. Model numbers and units

Find a title where numbers and letters are stuck together in a way that hurts search. What happens when someone searches for just the number or just the unit?

Your input:
Your output:
Better output:
Why it matters:

### 4. Hyphenated attributes

Find a title with a hyphenated word. What happens to it? Does splitting help or hurt retrieval?

Your input:
Your output:
Better output:
Why it matters:

### 5. Stopword damage

Find a title where removing common English words changes what the product actually is. The "better" output here might mean keeping a word your stopword list removes.

Your input:
Your output:
Better output:
Why it matters:

### 6. Code-switched language

Code-switching means mixing two languages in one sentence — common in Indian e-commerce titles (English + Hindi, English + Tamil, etc.). Find a real product title from an Indian e-commerce site that mixes languages. What does your tokenizer do with it?

Your input:
Your output:
Better output:
Why it matters:

### 7. Unicode and accents

Find a product title with special characters (brand names, special punctuation, diacritics). Does your tokenizer handle them or silently drop information?

Your input:
Your output:
Better output:
Why it matters:

### 8. Vocabulary explosion

Show a before-and-after vocabulary size for one bad normalization choice. Use the CLI to measure:

```bash
python -m indexzero vocab --csv data/flipkart_titles_tiny.csv --no-lowercase
python -m indexzero vocab --csv data/flipkart_titles_tiny.csv
```

Config A (bad):
Vocab size:
Config B (better):
Vocab size:
What changed and why:

## Reflection

1. Which failure surprised you the most?
2. Which tokenizer decision still feels uncertain?
3. Did any failure make you want to change a decision from your decision log?
