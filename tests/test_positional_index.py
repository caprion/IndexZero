from __future__ import annotations

from indexzero.query_processing import build_positional_index
from indexzero.text_processing import TokenizerConfig, tokenize_document


def test_positions_preserve_token_order() -> None:
    document = tokenize_document(
        "d1",
        "Wireless earbuds with wireless charging case",
        TokenizerConfig(),
    )
    positional_index = build_positional_index([document])

    wireless_posting = positional_index.postings["wireless"][0]
    earbuds_posting = positional_index.postings["earbuds"][0]

    assert wireless_posting.doc_id == "d1"
    assert wireless_posting.term_frequency == 2
    assert wireless_posting.positions == [0, 3]
    assert earbuds_posting.positions == [1]
