"""Relevance judgment I/O helpers (M4).

Load and save qrels (query relevance judgments) in CSV format.
Supports both numeric grades and ESCI letter labels.

Students: This file is GIVEN to you. Do not modify it.
"""

from __future__ import annotations

import csv
from pathlib import Path

from .contracts import RelevanceJudgment

# Amazon ESCI label mapping: letter -> integer grade
ESCI_GRADE_MAP: dict[str, int] = {
    "E": 3,  # Exact
    "S": 2,  # Substitute
    "C": 1,  # Complement
    "I": 0,  # Irrelevant
}


def load_qrels(path: Path) -> list[RelevanceJudgment]:
    """Load relevance judgments from a CSV file.

    Auto-detects the format by inspecting the header:
        - Numeric format: query_id,doc_id,relevance (int grade)
        - ESCI format: query_id,product_id,esci_label (E/S/C/I letter)

    Args:
        path: Path to the CSV file.

    Returns:
        List of RelevanceJudgment objects.

    Raises:
        ValueError: If the CSV has fewer than 3 columns or an unknown
            ESCI label is encountered.
    """
    judgments: list[RelevanceJudgment] = []

    with Path(path).open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            return judgments

        fieldnames = [f.strip() for f in reader.fieldnames]

        # Detect ESCI format by checking if the third column is esci_label
        is_esci = "esci_label" in fieldnames

        for row in reader:
            # Skip blank or comment lines
            raw_first = next(iter(row.values()), None) if row else None
            if raw_first is None or raw_first.strip().startswith("#"):
                continue

            # Strip keys to handle any whitespace in headers
            row = {k.strip(): v.strip() for k, v in row.items() if k is not None}

            if is_esci:
                query_id = row["query_id"]
                doc_id = row["product_id"]
                label = row["esci_label"].upper()
                if label not in ESCI_GRADE_MAP:
                    msg = f"Unknown ESCI label: {label!r}"
                    raise ValueError(msg)
                relevance = ESCI_GRADE_MAP[label]
            else:
                query_id = row["query_id"]
                doc_id = row["doc_id"]
                relevance = int(row["relevance"])

            judgments.append(
                RelevanceJudgment(
                    query_id=query_id,
                    doc_id=doc_id,
                    relevance=relevance,
                )
            )

    return judgments


def save_qrels(judgments: list[RelevanceJudgment], path: Path) -> None:
    """Save relevance judgments to a CSV file in numeric format.

    Output format: query_id,doc_id,relevance

    Args:
        judgments: List of RelevanceJudgment objects to save.
        path: Output file path.
    """
    with Path(path).open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["query_id", "doc_id", "relevance"])
        for j in judgments:
            writer.writerow([j.query_id, j.doc_id, j.relevance])
