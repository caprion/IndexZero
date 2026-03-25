"""Indexer -- the core of M2.

Students implement two functions here:
    1. build_index    -- turn tokenized documents into an inverted index
    2. lookup         -- retrieve the posting list for a single term

Each function has a docstring explaining what it should do and what
invariants the tests check. Start with the simplest version that works
(a dict of lists), then inspect the results.

Run tests as you go:
    pytest tests/test_indexer.py -v

Optional bonus (after core tests pass):
    3. save_index  -- serialize an index to a JSON file
    4. load_index  -- deserialize an index from a JSON file
"""

from __future__ import annotations

from pathlib import Path

from indexzero.text_processing.contracts import TokenizedDocument

from .contracts import InvertedIndex, Posting


def build_index(documents: list[TokenizedDocument]) -> InvertedIndex:
    """Build an inverted index from a list of tokenized documents.

    For each document, record which terms it contains and how often.
    The result is a mapping from every term in the corpus to a list
    of Posting objects (one per document that contains the term).

    Also record each document's token count in document_lengths, so
    downstream modules (BM25) can normalize for document length.

    Args:
        documents: Output of M1 -- a list of TokenizedDocument objects.

    Returns:
        An InvertedIndex with populated postings and document metadata.

    Invariants (tested automatically):
        - Every term in any document has a key in postings.
        - Each posting list has exactly one Posting per document.
        - posting.term_frequency matches the document's term_counts[term].
        - document_lengths[doc_id] == document.token_count for every doc.
        - document_count == len(documents).
        - total_terms == sum of all document token counts.
        - Posting lists are sorted by doc_id (deterministic output).
    """
    raise NotImplementedError("Students implement this in M2.")


def lookup(index: InvertedIndex, term: str) -> list[Posting]:
    """Retrieve the posting list for a single term.

    This is the payoff of indexing: instead of scanning every document
    to find which ones contain a term, you jump straight to the answer.

    Args:
        index: A built InvertedIndex.
        term: The term to look up (must already be normalized/tokenized).

    Returns:
        The list of Posting objects for the term.
        Returns an empty list if the term is not in the index.
    """
    raise NotImplementedError("Students implement this in M2.")


# ---------------------------------------------------------------------------
# Optional / bonus: persistence
# ---------------------------------------------------------------------------

def save_index(index: InvertedIndex, path: Path) -> None:
    """Serialize an InvertedIndex to a JSON file.

    Hint: use the helpers in indexing/serialization.py (given to you)
    to convert the index to a JSON-safe dict, then write it with json.dump.

    Args:
        index: The index to save.
        path: File path to write (will be created or overwritten).
    """
    raise NotImplementedError("Students implement this in M2 (bonus).")


def load_index(path: Path) -> InvertedIndex:
    """Deserialize an InvertedIndex from a JSON file.

    Hint: read the JSON with json.load, then use the helpers in
    indexing/serialization.py to reconstruct the InvertedIndex.

    Args:
        path: Path to a JSON file previously written by save_index.

    Returns:
        The reconstructed InvertedIndex.
    """
    raise NotImplementedError("Students implement this in M2 (bonus).")
