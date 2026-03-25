# M2 Decision Log

Record your design choices for the inverted index. For each decision, write what you chose, what alternatives you considered, and why.

## 1. Posting list order

**Your choice:**

_[How are your posting lists ordered? By doc_id? By term frequency? Insertion order? Something else?]_

**Why:**

_[What does this ordering enable or prevent? What would change if you chose differently?]_

## 2. Missing-term behavior

**Your choice:**

_[What does your `lookup` function return for a term not in the index?]_

**Why:**

_[Why this behavior? What would break in M3 if you raised an exception instead?]_

## 3. Terms as strings vs token IDs

**Your choice:**

_[Your postings dict uses string keys. The Vocabulary from M1 has a token_to_id mapping. Why use strings instead of integer IDs?]_

**Why:**

_[What are the tradeoffs? When would integer IDs be better?]_

## 4. What belongs in the index vs derived at query time?

**Your choice:**

_[Your InvertedIndex stores postings, document_lengths, document_count, total_terms. The average_document_length is computed. What else could you store vs compute?]_

**Why:**

_[Why store document_lengths instead of computing them from postings? Why compute average instead of storing it?]_

## 5. Non-positional index

**Your choice:**

_[Your Posting has doc_id and term_frequency. It does NOT record where in the document the term appears.]_

**Why:**

_[What capability is impossible without positions? When would you add them? What's the cost?]_

## 6. Serialization format (bonus — if you implemented save/load)

**Your choice:**

_[JSON? Binary? Something else?]_

**Why:**

_[What did you optimize for — human readability, file size, load speed? What would a production system choose?]_
