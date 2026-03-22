"""Public API for the text_processing package.

All names here are importable as:
    from indexzero.text_processing import TokenizerConfig, tokenize_text, ...
"""

from .contracts import TokenizedDocument, TokenizerConfig, Vocabulary
from .tokenizer import normalize_text, tokenize_document, tokenize_text
from .vocabulary import build_vocabulary

__all__ = [
    "TokenizedDocument",
    "TokenizerConfig",
    "Vocabulary",
    "build_vocabulary",
    "normalize_text",
    "tokenize_document",
    "tokenize_text",
]
