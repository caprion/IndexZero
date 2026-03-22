# M1 Decision Log

Record every material preprocessing choice here. The code is not the deliverable — this log is.

> **Weak entry:** "I added lowercasing because it's standard."
>
> **Strong entry:** "I added lowercasing. Vocabulary dropped from 847 to 612 unique terms. But 'HP' (the brand) and 'hp' (horsepower in a blender title) are now the same token. That means a search for 'HP laptop' will match 'hp motor 750W mixer grinder'. I'm keeping it because the vocabulary reduction is worth the ambiguity for now. I'll revisit if M3 ranking shows cross-category contamination."

## How to fill this in

For each decision:

1. **What choice did you make?** — Be specific. Not "I normalize text" but "I replace `/` and `-` with spaces."
2. **What went wrong before you got here?** — Describe a bug, a wrong output, or a test failure you hit along the way. Paste the terminal output. This is worth more than listing alternatives you never actually tried.
3. **What evidence drove the choice?** — Run your pipeline and show numbers. Use the CLI to measure:
   ```bash
   # Vocabulary size with your current config:
   python -m indexzero vocab --csv data/flipkart_titles_tiny.csv
   # Compare with a different config:
   python -m indexzero vocab --csv data/flipkart_titles_tiny.csv --drop-stopwords
   ```
   Then write something like: "Vocabulary went from 62 to 48 unique terms after stopword removal."
4. **What could break this?** — Name a concrete scenario where this choice hurts.

## Decisions

| Decision | What went wrong first | Why I chose this (with evidence) | What would break this |
|---|---|---|---|
| Lowercasing strategy | | | |
| Punctuation / separator handling | | | |
| Hyphen and slash treatment | | | |
| Numeric boundary handling | | | |
| Stopword policy | | | |
| Stemming strategy | | | |
| Unicode normalization form | | | |
| Brand / model token treatment | | | |

## Hints used

List which hint files you opened (if any). No penalty for using them — but
note what you tried before opening the hint and what you learned from it.

| Hint file | What I tried first | What the hint taught me |
|---|---|---|
| | | |

## Reflection

After completing all decisions, answer:

1. Which decision are you least confident about? Why?
2. If you could only keep three normalization steps, which three and why?
3. What would you change if your corpus were 10,000 academic paper titles instead of product listings?
