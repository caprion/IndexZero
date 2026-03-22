"""Vocabulary builder — corpus-level statistics from tokenized documents.

Students implement one function here:
    build_vocabulary — aggregate token statistics across a list of documents.

Run tests:
    pytest tests/test_vocabulary.py -v
"""

# This line lets you write list[str] instead of List[str] on Python 3.9.
from __future__ import annotations

# The dot means "from this same package." Use pytest or python -m indexzero to run.
from .contracts import TokenizedDocument, Vocabulary


def build_vocabulary(documents: list[TokenizedDocument]) -> Vocabulary:
    """Build corpus-level vocabulary statistics from tokenized documents.

    This function should:
    1. Iterate over all documents.
    2. For each document, update:
       - document_frequency: number of documents containing each token
       - collection_frequency: total count of each token across all documents
    3. Assign a stable integer ID to each token (sorted alphabetically, starting at 1).
    4. Compute total_terms (sum of all token occurrences).
    5. Return a Vocabulary with all fields populated.

    Invariants (tested automatically):
    - vocabulary.document_count == len(documents)
    - vocabulary.total_terms == sum of all token counts across all documents
    - Every token that appears in any document has an entry in token_to_id
    - document_frequency[token] <= document_count for all tokens

    Args:
        documents: A list of TokenizedDocument instances from M1's tokenizer.

    Returns:
        A Vocabulary instance with corpus-level statistics.
    """
    raise NotImplementedError("Students implement this in M1.")
