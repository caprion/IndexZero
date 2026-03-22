# M1 → M3 Consequence Chain

One codebase grows across modules. Your M1 tokenizer choices have real consequences in M3 (BM25 Ranking) and M4 (Evaluation). This exercise asks you to **predict** those consequences before you see them.

## How this works

1. Read each scenario below.
2. **Predict** what will happen. Write your prediction before running anything.
3. When you reach M3, **verify** by running the actual code.
4. Compare your prediction to reality. The gap is where the learning lives.

## Scenario 1: Stopwords and BM25

BM25 uses term frequency (tf) and inverse document frequency (idf) to score documents. Common terms get low idf scores.

**Setup:** Your M1 tokenizer has `drop_stopwords=False`.

**Question:** In M3, you run the query `"shoes for men"`. The word "for" appears in almost every document.

- **Predict:** How does "for" affect the BM25 score? Does it help, hurt, or make no difference? Why?
- **Predict:** Would enabling `drop_stopwords=True` change the ranking order? If so, how?

Your prediction:

_[Write your prediction here before reaching M3]_

Your verification (fill in at M3):

_[What actually happened]_

## Scenario 2: Stemming and query matching

**Setup:** Your M1 tokenizer uses `stemming="suffix"`.

**Question:** A user searches for `"running shoes"`. Your stemmer reduces "running" to something shorter. A document title says "Runners World Marathon Training."

- **Predict:** Does the stemmed query match this document? Should it?
- **Predict:** Give an example of a title that SHOULDN'T match "running shoes" but DOES because of your stemmer.

Your prediction:

_[Write your prediction here before reaching M3]_

Your verification (fill in at M3):

_[What actually happened]_

## Scenario 3: Vocabulary size and ranking discrimination

**Setup:** You compare two tokenizer configs:
- Config A: `lowercase=True, drop_stopwords=False, stemming="none"` (larger vocabulary)
- Config B: `lowercase=True, drop_stopwords=True, stemming="suffix"` (smaller vocabulary)

**Question:** Config B has fewer unique tokens. Fewer unique tokens means fewer distinct idf values.

- **Predict:** Which config gives BM25 more ability to distinguish between documents? Why?
- **Predict:** Is a smaller vocabulary always better or always worse for ranking? Or does it depend?

Your prediction:

_[Write your prediction here before reaching M3]_

Your verification (fill in at M3):

_[What actually happened]_

## Scenario 4: Numeric tokens and product search

**Setup:** Your tokenizer normalizes `"8GB"` into either `["8gb"]` (one token) or `["8", "gb"]` (two tokens), depending on `split_numeric_boundaries`.

**Question:** A user searches for `"8GB RAM"`.

- **Predict:** How does the split/no-split choice affect whether this query matches `"16GB RAM"` or `"8TB SSD"`?
- **Predict:** Which choice is better for product search? Why?

Your prediction:

_[Write your prediction here before reaching M3]_

Your verification (fill in at M3):

_[What actually happened]_

## Reflection (fill in after M3 verification)

1. How many of your predictions were correct?
2. Which prediction was most wrong? What did you misunderstand?
3. If you could go back and change one M1 decision based on M3 results, what would it be?
