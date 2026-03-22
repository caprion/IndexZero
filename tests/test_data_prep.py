from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from indexzero.data_prep import prepare_amazon_esci, prepare_flipkart_titles


class DataPrepTests(unittest.TestCase):
    def test_prepare_flipkart_titles_standardizes_columns(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_path = temp_path / "raw.csv"
            output_path = temp_path / "prepared.csv"

            with input_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["sku", "name"])
                writer.writeheader()
                writer.writerow({"sku": "sku-1", "name": "Boat Airdopes 141"})

            prepared = prepare_flipkart_titles(
                input_path=input_path,
                output_path=output_path,
                text_column="name",
                doc_id_column="sku",
            )

            self.assertEqual(prepared.row_count, 1)
            self.assertTrue(output_path.exists())
            with output_path.open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[0]["product_id"], "sku-1")
            self.assertEqual(rows[0]["title"], "Boat Airdopes 141")

    def test_prepare_amazon_esci_filters_to_limited_queries(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            products_path = temp_path / "products.csv"
            queries_path = temp_path / "queries.csv"
            labels_path = temp_path / "labels.csv"
            output_dir = temp_path / "prepared"

            with products_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["product_id", "title"])
                writer.writeheader()
                writer.writerow({"product_id": "p1", "title": "Wireless Earbuds"})
                writer.writerow({"product_id": "p2", "title": "Steel Bottle"})

            with queries_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["query_id", "query"])
                writer.writeheader()
                writer.writerow({"query_id": "q1", "query": "earbuds"})
                writer.writerow({"query_id": "q2", "query": "bottle"})

            with labels_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["query_id", "product_id", "esci_label"])
                writer.writeheader()
                writer.writerow({"query_id": "q1", "product_id": "p1", "esci_label": "E"})
                writer.writerow({"query_id": "q2", "product_id": "p2", "esci_label": "E"})

            prepared_files = prepare_amazon_esci(
                products_path=products_path,
                queries_path=queries_path,
                labels_path=labels_path,
                output_dir=output_dir,
                limit=1,
            )

            self.assertEqual(len(prepared_files), 3)
            with (output_dir / "queries.csv").open("r", encoding="utf-8", newline="") as handle:
                queries = list(csv.DictReader(handle))
            with (output_dir / "products.csv").open("r", encoding="utf-8", newline="") as handle:
                products = list(csv.DictReader(handle))
            self.assertEqual(len(queries), 1)
            self.assertEqual(queries[0]["query_id"], "q1")
            self.assertEqual(len(products), 1)
            self.assertEqual(products[0]["product_id"], "p1")


if __name__ == "__main__":
    unittest.main()
