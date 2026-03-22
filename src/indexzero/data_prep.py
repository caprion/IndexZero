from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PreparedFile:
    path: Path
    row_count: int


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def _write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> PreparedFile:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return PreparedFile(path=path, row_count=len(rows))


def prepare_flipkart_titles(
    input_path: Path,
    output_path: Path,
    text_column: str,
    doc_id_column: str | None = None,
    limit: int | None = None,
) -> PreparedFile:
    rows = _read_csv_rows(input_path)
    if not rows:
        return _write_csv_rows(output_path, ["product_id", "title"], [])

    if text_column not in rows[0]:
        raise ValueError(f"Column '{text_column}' not found in {input_path}.")

    prepared_rows: list[dict[str, str]] = []
    for index, row in enumerate(rows, start=1):
        title = row[text_column].strip()
        if not title:
            continue
        product_id = row[doc_id_column].strip() if doc_id_column else f"flipkart-{index:06d}"
        prepared_rows.append({"product_id": product_id, "title": title})
        if limit is not None and len(prepared_rows) >= limit:
            break

    return _write_csv_rows(output_path, ["product_id", "title"], prepared_rows)


def prepare_amazon_esci(
    products_path: Path,
    queries_path: Path,
    labels_path: Path,
    output_dir: Path,
    limit: int | None = None,
) -> list[PreparedFile]:
    product_rows = _read_csv_rows(products_path)
    query_rows = _read_csv_rows(queries_path)
    label_rows = _read_csv_rows(labels_path)

    normalized_products = [
        {
            "product_id": row.get("product_id", "").strip(),
            "title": (row.get("title") or row.get("product_title") or "").strip(),
        }
        for row in product_rows
    ]
    normalized_queries = [
        {
            "query_id": (row.get("query_id") or f"query-{index:06d}").strip(),
            "query": row.get("query", "").strip(),
        }
        for index, row in enumerate(query_rows, start=1)
    ]
    normalized_labels = [
        {
            "query_id": row.get("query_id", "").strip(),
            "product_id": row.get("product_id", "").strip(),
            "esci_label": (row.get("esci_label") or row.get("label") or "").strip(),
        }
        for row in label_rows
    ]

    if limit is not None:
        kept_queries = normalized_queries[:limit]
        kept_query_ids = {row["query_id"] for row in kept_queries}
        normalized_labels = [row for row in normalized_labels if row["query_id"] in kept_query_ids]
        kept_product_ids = {row["product_id"] for row in normalized_labels}
        normalized_products = [row for row in normalized_products if row["product_id"] in kept_product_ids]
        normalized_queries = kept_queries

    return [
        _write_csv_rows(output_dir / "products.csv", ["product_id", "title"], normalized_products),
        _write_csv_rows(output_dir / "queries.csv", ["query_id", "query"], normalized_queries),
        _write_csv_rows(
            output_dir / "relevance_labels.csv",
            ["query_id", "product_id", "esci_label"],
            normalized_labels,
        ),
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="prepare_course_data")
    subparsers = parser.add_subparsers(dest="command", required=True)

    flipkart_parser = subparsers.add_parser("flipkart-titles", help="Standardize Flipkart-style titles.")
    flipkart_parser.add_argument("--input", required=True, type=Path)
    flipkart_parser.add_argument("--output", required=True, type=Path)
    flipkart_parser.add_argument("--text-column", required=True)
    flipkart_parser.add_argument("--doc-id-column")
    flipkart_parser.add_argument("--limit", type=int)

    esci_parser = subparsers.add_parser("amazon-esci", help="Standardize the course ESCI files.")
    esci_parser.add_argument("--products", required=True, type=Path)
    esci_parser.add_argument("--queries", required=True, type=Path)
    esci_parser.add_argument("--labels", required=True, type=Path)
    esci_parser.add_argument("--output-dir", required=True, type=Path)
    esci_parser.add_argument("--limit", type=int)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "flipkart-titles":
        prepared = prepare_flipkart_titles(
            input_path=args.input,
            output_path=args.output,
            text_column=args.text_column,
            doc_id_column=args.doc_id_column,
            limit=args.limit,
        )
        print(f"Wrote {prepared.row_count} rows to {prepared.path}")
        return

    if args.command == "amazon-esci":
        prepared_files = prepare_amazon_esci(
            products_path=args.products,
            queries_path=args.queries,
            labels_path=args.labels,
            output_dir=args.output_dir,
            limit=args.limit,
        )
        for prepared in prepared_files:
            print(f"Wrote {prepared.row_count} rows to {prepared.path}")
        return

    raise ValueError(f"Unsupported command: {args.command}")
