"""Placeholder for course data preparation utilities.

When larger datasets (1K Flipkart titles, ESCI 2K) are available,
this script will download and shape them into the course format.

Usage:
    python scripts/prepare_course_data.py

For now, the tiny dataset (data/flipkart_titles_tiny.csv) is
committed to the repo and sufficient for all M1 work.
"""

from __future__ import annotations

import sys


def main() -> None:
    print("Course data preparation")
    print("=" * 40)
    print()
    print("The tiny dataset (8 rows) is already in data/flipkart_titles_tiny.csv")
    print("and is sufficient for M1 implementation and all unit tests.")
    print()
    print("Larger datasets for assessment exercises:")
    print("  - flipkart_titles_1k.csv  (1,000 Flipkart titles)")
    print("  - amazon_esci_2k/         (2,000 ESCI query-product pairs)")
    print()
    print("These will be available in a future update.")
    print("See data/README.md for details on the dataset strategy.")


if __name__ == "__main__":
    main()
