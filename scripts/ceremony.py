"""Part 1 Ceremony: Your Search Engine Works.

Run this after completing M0-M4 to see your entire pipeline in action.
One script, three acts, your code.

Usage:
    python scripts/ceremony.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Setup: make sure the package is importable
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

try:
    from indexzero.text_processing import (
        TokenizerConfig,
        tokenize_document,
        tokenize_text,
    )
    from indexzero.indexing import build_index, InvertedIndex
    from indexzero.scoring import search, ScorerConfig
    from indexzero.evaluation import (
        EvalReport,
        evaluate,
        load_qrels,
        QueryResults,
    )
except (ImportError, ModuleNotFoundError) as exc:
    print(f"Import failed: {exc}")
    print("Make sure you are running from the repository root.")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MOVIES_CSV = REPO_ROOT / "data" / "movies" / "movies.csv"
QUERIES_CSV = REPO_ROOT / "data" / "movies" / "queries.csv"
QRELS_CSV = REPO_ROOT / "data" / "movies" / "qrels.csv"

TOK_CONFIG = TokenizerConfig(
    lowercase=True,
    drop_stopwords=True,
    stemming="none",
)

SCORER_CONFIG = ScorerConfig(k1=1.2, b=0.75)
K = 5

# Hand-picked queries that BM25 handles well (Act 1)
ACT1_QUERIES = [
    ("mq-006", "prison escape freedom"),
    ("mq-005", "war soldiers battle"),
    ("mq-014", "courtroom jury trial"),
    ("mq-015", "dinosaur island park"),
    ("mq-003", "detective murder investigation"),
]

# Semantic queries that BM25 struggles with (Act 3)
ACT3_QUERIES = [
    ("mq-021", "feel-good movie for a rainy day"),
    ("mq-022", "movie that makes you think about life differently"),
    ("mq-023", "underdog story overcoming impossible odds"),
]


def _separator(char: str = "=", width: int = 64) -> str:
    return char * width


def _build_movie_index() -> tuple[InvertedIndex, dict[str, str]]:
    """Tokenize movies and build the inverted index. Returns (index, titles)."""
    titles: dict[str, str] = {}
    documents = []
    with MOVIES_CSV.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            did = row["doc_id"].strip()
            titles[did] = row["title"].strip()
            doc = tokenize_document(
                doc_id=did,
                text=row["text"].strip(),
                config=TOK_CONFIG,
            )
            documents.append(doc)
    index = build_index(documents)
    return index, titles


def _search_and_display(
    query_text: str,
    index: InvertedIndex,
    titles: dict[str, str],
    top_k: int = K,
) -> list[str]:
    """Search and print results. Returns list of doc_ids."""
    terms = tokenize_text(query_text, TOK_CONFIG)
    results = search(terms, index, SCORER_CONFIG, top_k=top_k)
    for rank, sr in enumerate(results, 1):
        title = titles.get(sr.doc_id, sr.doc_id)
        print(f"  {rank}. {title}")
    if not results:
        print("  (no results)")
    return [r.doc_id for r in results]


def _run_eval(
    index: InvertedIndex,
    qrels: dict,
) -> EvalReport:
    """Run full evaluation and return the report."""
    queries: list[tuple[str, str]] = []
    with QUERIES_CSV.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            queries.append((row["query_id"].strip(), row["query"].strip()))

    all_results: list[QueryResults] = []
    for query_id, query_text in queries:
        terms = tokenize_text(query_text, TOK_CONFIG)
        hits = search(terms, index, SCORER_CONFIG, top_k=K)
        doc_ids = [r.doc_id for r in hits]
        all_results.append(QueryResults(query_id=query_id, doc_ids=doc_ids))

    report = evaluate(all_results, qrels, k=K, relevance_threshold=2)
    return report


def act1(index: InvertedIndex, titles: dict[str, str]) -> None:
    """Act 1 -- The Feeling. Interactive search, visible results."""
    print()
    print(_separator("-"))
    print("  Act 1: The Feeling")
    print(_separator("-"))
    print()
    print("Let's see what your search engine can find.")
    print()

    for _qid, query_text in ACT1_QUERIES:
        print(f'  Query: "{query_text}"')
        _search_and_display(query_text, index, titles, top_k=3)
        print()

    print("Your search engine found the right movies. You built this.")


def act2(index: InvertedIndex, qrels: dict, titles: dict[str, str]) -> None:
    """Act 2 -- The Proof. Evaluation metrics across all 25 queries."""
    print()
    print(_separator("-"))
    print("  Act 2: The Proof")
    print(_separator("-"))
    print()
    print(f"Running evaluation on 25 judged queries (k={K})...")
    print()

    report = _run_eval(index, qrels)

    print(f"  P@{K}:    {report.mean_precision_at_k:.4f}")
    print(f"  R@{K}:    {report.mean_recall_at_k:.4f}")
    print(f"  MRR:     {report.mean_reciprocal_rank:.4f}")
    print(f"  nDCG@{K}: {report.mean_ndcg_at_k:.4f}")
    print()

    # Plain-English interpretation
    approx_relevant = report.mean_precision_at_k * K
    mrr_pos = 1 / report.mean_reciprocal_rank if report.mean_reciprocal_rank > 0 else K
    print(f"  What this means: about {approx_relevant:.1f} of the top {K} results")
    print(f"  are relevant on average, and a good result usually appears")
    if mrr_pos <= 2:
        print(f"  in the first couple of positions.")
    else:
        print(f"  within the first {mrr_pos:.0f} positions.")
    print()

    # Show per-query scores for Act 1 queries — include query text
    act1_lookup = {qid: qt for qid, qt in ACT1_QUERIES}
    print("  Per-query scores for the searches you just saw:")
    for qm in report.per_query:
        if qm.query_id in act1_lookup:
            qt = act1_lookup[qm.query_id]
            print(f'    "{qt}"  nDCG={qm.ndcg_at_k:.3f}  P@{K}={qm.precision_at_k:.3f}')
    print()
    print(
        f"Your search engine scores {report.mean_ndcg_at_k:.2f} nDCG "
        f"across {report.num_queries} queries."
    )
    print("Not perfect, but it works. And you can measure exactly where it struggles.")


def act3(index: InvertedIndex, qrels: list, titles: dict[str, str]) -> None:
    """Act 3 -- The Gap. Semantic queries that BM25 cannot handle."""
    print()
    print(_separator("-"))
    print("  Act 3: The Gap")
    print(_separator("-"))
    print()
    print("Now try these queries:")
    print()

    # Build lookup: query_id -> {doc_id: relevance}
    qrels_by_query: dict[str, dict[str, int]] = {}
    for j in qrels:
        qrels_by_query.setdefault(j.query_id, {})[j.doc_id] = j.relevance

    for query_id, query_text in ACT3_QUERIES:
        print(f'  Query: "{query_text}"')
        doc_ids = _search_and_display(query_text, index, titles, top_k=3)

        # Compute nDCG for just this query
        qr = QueryResults(query_id=query_id, doc_ids=doc_ids)
        report = evaluate([qr], qrels, k=K, relevance_threshold=2)
        if report.per_query:
            ndcg = report.per_query[0].ndcg_at_k
            print(f"  nDCG: {ndcg:.3f}")

        # Show what relevant movies exist for this query
        judgments = qrels_by_query.get(query_id, {})
        relevant = [did for did, grade in judgments.items() if grade >= 2]
        if relevant:
            names = [titles.get(did, did) for did in relevant[:4]]
            print(f"  Expected: {', '.join(names)}")
        print()

    print("Your engine matched keywords, not meaning.")
    print("It found literal words but missed the intent behind the query.")
    print()
    print("This is why Part 2 exists.")
    print("M5-M9 teach your engine to understand, not just match.")


def main() -> None:
    print()
    print(_separator())
    print("  Part 1 Ceremony: Your Search Engine Works")
    print(_separator())

    # Verify data files exist
    for path in (MOVIES_CSV, QUERIES_CSV, QRELS_CSV):
        if not path.exists():
            print(f"Missing data file: {path}")
            sys.exit(1)

    print()
    print("Loading 150 movie plot summaries...")

    try:
        index, titles = _build_movie_index()
    except NotImplementedError as exc:
        print(f"\nNot ready yet: {exc}")
        print("Complete M1-M4 before running the ceremony.")
        sys.exit(1)

    term_count = len(index.postings) if hasattr(index, "postings") else "?"
    print(f"Tokenized and indexed. {term_count} unique terms in the index.")

    qrels = load_qrels(QRELS_CSV)

    try:
        act1(index, titles)
    except NotImplementedError as exc:
        print(f"\nAct 1 failed: {exc}")
        print("Check your scoring module (M3).")
        return

    try:
        act2(index, qrels, titles)
    except NotImplementedError as exc:
        print(f"\nAct 2 failed: {exc}")
        print("Check your evaluation module (M4).")
        return

    try:
        act3(index, qrels, titles)
    except NotImplementedError as exc:
        print(f"\nAct 3 failed: {exc}")
        print("Check your evaluation module (M4).")
        return

    print()
    print(_separator())
    print("  Part 1 complete. You built a search engine from scratch.")
    print()
    print("  Want to search your own data? Any CSV with doc_id and text")
    print("  columns works with the indexer. In M8, you will build the")
    print("  pipeline that ingests raw files automatically.")
    print(_separator())
    print()


if __name__ == "__main__":
    main()
