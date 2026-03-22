# Ranking Audit Worksheet

Use this worksheet for M0. Write like an engineer doing a product audit, not like someone trying to guess the "right" answer.

## Student

- Name:
- Chosen site:
- Date:

## Quick framing

- In one line: what kind of system are you looking at?  
  Example: "An e-commerce search API returning ranked product results."
- What kinds of matching clues seem most visible from the page: exact words, category fit, brand fit, popularity, sponsorship, or broader similarity?  
  Keep this to 2-3 lines. Stay observational. If you make an architecture guess, mark it as low-confidence.

## Query set

| Query type | Query | Why you chose it | Likely user intent |
| --- | --- | --- | --- |
| Broad |  |  |  |
| Specific |  |  |  |
| Ambiguous |  |  |  |

## Query 1 audit

| Rank | Result | What probably matched? | Evidence you can point to | Likely signals | Alternative explanation | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 |  |  |  |  |  | High / Med / Low |
| 2 |  |  |  |  |  | High / Med / Low |
| 3 |  |  |  |  |  | High / Med / Low |

- `What probably matched?` = the visible clue in the query/result pair.
- `Likely signals` = the broader ranking factors you think the system may be using.

- Quick note: which result looked most useful to the user, and why?

## Query 2 audit

| Rank | Result | What probably matched? | Evidence you can point to | Likely signals | Alternative explanation | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 |  |  |  |  |  | High / Med / Low |
| 2 |  |  |  |  |  | High / Med / Low |
| 3 |  |  |  |  |  | High / Med / Low |

- Quick note: which result looked most useful to the user, and why?

## Query 3 audit

| Rank | Result | What probably matched? | Evidence you can point to | Likely signals | Alternative explanation | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 |  |  |  |  |  | High / Med / Low |
| 2 |  |  |  |  |  | High / Med / Low |
| 3 |  |  |  |  |  | High / Med / Low |

- Quick note: which result looked most useful to the user, and why?

## One surprising result

- Result:
- Why it surprised you:
- What signal or failure mode might explain it:
- What evidence supports your guess:
- What are you still unsure about:

## Comparison exercise: same query, different goal

Pick one query from above and compare how the ranking should change under two system goals.

- Chosen query:

| System goal | What should rank first? | What signals should matter more? | What should move down? | Why |
| --- | --- | --- | --- | --- |
| Help the user buy fast with high confidence |  |  |  |  |
| Help the user explore options or discover alternatives |  |  |  |  |

## What signals do you think this search engine uses?

Write one short paragraph. Be concrete. Good answers name likely signals such as exact term match, brand match, category fit, popularity, price, discounting, ratings, review count, delivery promise, sponsorship, freshness, or personalization.

## What are you least certain about?

List one thing you suspect but cannot explain yet.

## Light foreshadowing for later

Without using formal metrics yet, make a quick judgment for each query's top result:

| Query | Top result | Your quick judgment |
| --- | --- | --- |
| Broad |  | Clearly useful / Maybe useful / Not useful |
| Specific |  | Clearly useful / Maybe useful / Not useful |
| Ambiguous |  | Clearly useful / Maybe useful / Not useful |

One line each: why did you label it that way?

These labels are intentionally simpler than the formal relevance judgments you will meet later in the course.
