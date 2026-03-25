"""IndexZero CLI entry point.

Usage:
    python -m indexzero tokenize --text "Nike running shoes for men"
    python -m indexzero vocab --csv data/flipkart_titles_tiny.csv --text-column title
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from .text_processing import (
    TokenizerConfig,
    build_vocabulary,
    tokenize_document,
    tokenize_text,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="indexzero",
        description="IndexZero — a search engine you build from scratch.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- tokenize ----------------------------------------------------------
    tok = subparsers.add_parser("tokenize", help="Tokenize a single text string.")
    tok.add_argument("--text", required=True, help="Text to tokenize.")
    tok.add_argument(
        "--no-lowercase",
        action="store_true",
        help="Disable lowercasing.",
    )
    tok.add_argument(
        "--drop-stopwords",
        action="store_true",
        help="Remove common English stopwords.",
    )
    tok.add_argument(
        "--stemming",
        choices=["none", "suffix"],
        default="none",
        help="Stemming strategy (default: none).",
    )
    tok.add_argument(
        "--strip-accents",
        action="store_true",
        help="Strip accent marks from characters.",
    )
    tok.add_argument(
        "--split-numeric",
        action="store_true",
        help="Split on numeric boundaries (e.g., 8GB -> 8 gb).",
    )

    # --- vocab -------------------------------------------------------------
    voc = subparsers.add_parser("vocab", help="Build vocabulary from a CSV file.")
    voc.add_argument("--csv", required=True, type=Path, help="Path to CSV file.")
    voc.add_argument(
        "--text-column",
        default="title",
        help="Name of the text column (default: title).",
    )
    voc.add_argument(
        "--doc-id-column",
        default="product_id",
        help="Name of the document ID column (default: product_id).",
    )
    voc.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of documents to process.",
    )
    # Config flags — same as tokenize, so you can compare vocab across configs
    voc.add_argument(
        "--no-lowercase",
        action="store_true",
        help="Disable lowercasing.",
    )
    voc.add_argument(
        "--drop-stopwords",
        action="store_true",
        help="Remove common English stopwords.",
    )
    voc.add_argument(
        "--stemming",
        choices=["none", "suffix"],
        default="none",
        help="Stemming strategy (default: none).",
    )
    voc.add_argument(
        "--strip-accents",
        action="store_true",
        help="Strip accent marks from characters.",
    )
    voc.add_argument(
        "--split-numeric",
        action="store_true",
        help="Split on numeric boundaries (e.g., 8GB -> 8 gb).",
    )

    # --- index -------------------------------------------------------------
    idx = subparsers.add_parser("index", help="Build an inverted index from a CSV file.")
    idx.add_argument("--csv", required=True, type=Path, help="Path to CSV file.")
    idx.add_argument("--output", required=True, type=Path, help="Output path for index JSON.")
    idx.add_argument(
        "--text-column",
        default="title",
        help="Name of the text column (default: title).",
    )
    idx.add_argument(
        "--doc-id-column",
        default="product_id",
        help="Name of the document ID column (default: product_id).",
    )
    idx.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of documents to process.",
    )
    idx.add_argument("--no-lowercase", action="store_true", help="Disable lowercasing.")
    idx.add_argument("--drop-stopwords", action="store_true", help="Remove stopwords.")
    idx.add_argument("--stemming", choices=["none", "suffix"], default="none")
    idx.add_argument("--strip-accents", action="store_true")
    idx.add_argument("--split-numeric", action="store_true")

    # --- lookup ------------------------------------------------------------
    lkp = subparsers.add_parser("lookup", help="Look up a term in a built index.")
    lkp.add_argument("--index", required=True, type=Path, help="Path to index JSON file.")
    lkp.add_argument("--term", required=True, help="Term to look up.")

    return parser


def _load_csv_documents(
    csv_path: Path,
    text_column: str,
    doc_id_column: str,
    limit: int | None,
    config: TokenizerConfig,
) -> list:
    """Read a CSV and tokenize each row into a TokenizedDocument."""
    from .text_processing import TokenizedDocument  # noqa: F811

    documents = []
    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            doc = tokenize_document(
                doc_id=row[doc_id_column],
                text=row[text_column],
                config=config,
            )
            documents.append(doc)
            if limit is not None and len(documents) >= limit:
                break
    return documents


def _config_from_args(args: argparse.Namespace) -> TokenizerConfig:
    """Build a TokenizerConfig from CLI flags (shared by tokenize and vocab)."""
    return TokenizerConfig(
        lowercase=not args.no_lowercase,
        drop_stopwords=args.drop_stopwords,
        stemming=args.stemming,
        strip_accents=args.strip_accents,
        split_numeric_boundaries=args.split_numeric,
    )


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "tokenize":
        config = _config_from_args(args)
        tokens = tokenize_text(args.text, config)
        print(tokens)
        return

    if args.command == "vocab":
        config = _config_from_args(args)
        documents = _load_csv_documents(
            csv_path=args.csv,
            text_column=args.text_column,
            doc_id_column=args.doc_id_column,
            limit=args.limit,
            config=config,
        )
        vocabulary = build_vocabulary(documents)
        print(f"documents  = {vocabulary.document_count}")
        print(f"total_terms = {vocabulary.total_terms}")
        print(f"vocab_size  = {len(vocabulary.token_to_id)}")
        return

    if args.command == "index":
        from .indexing import build_index, save_index

        config = _config_from_args(args)
        documents = _load_csv_documents(
            csv_path=args.csv,
            text_column=args.text_column,
            doc_id_column=args.doc_id_column,
            limit=args.limit,
            config=config,
        )
        index = build_index(documents)
        save_index(index, args.output)
        print(f"documents   = {index.document_count}")
        print(f"unique_terms = {len(index.postings)}")
        print(f"total_terms  = {index.total_terms}")
        print(f"avg_doc_len  = {index.average_document_length:.1f}")
        print(f"saved to     = {args.output}")
        return

    if args.command == "lookup":
        from .indexing import load_index, lookup

        index = load_index(args.index)
        results = lookup(index, args.term)
        if not results:
            print(f"Term '{args.term}' not found in index.")
        else:
            print(f"Term '{args.term}' found in {len(results)} document(s):")
            for posting in results:
                print(f"  {posting.doc_id}  tf={posting.term_frequency}")
        return

    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
