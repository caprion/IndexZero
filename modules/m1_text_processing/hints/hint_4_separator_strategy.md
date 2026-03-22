# Hint 4: Separator strategy

## The problem

Product titles use hyphens ("non-stick"), slashes ("24cm/28cm"),
and apostrophes ("women's", "L'Oreal") as separators. Your tokenizer
needs a strategy for each, and the wrong choice breaks search.

## The concept

There are two basic strategies for each separator:
- **Replace with space** — splits the word into parts
- **Remove entirely** — joins the parts together

Each has trade-offs:

| Separator | Replace with space | Remove |
|---|---|---|
| Hyphen: "non-stick" | "non" + "stick" | "nonstick" |
| Slash: "24cm/28cm" | "24cm" + "28cm" | "24cm28cm" |
| Apostrophe: "women's" | "women" + "s" | "womens" |
| Apostrophe: "L'Oreal" | "L" + "Oreal" | "LOreal" |

## What to explore

1. If you replace hyphens with spaces, "USB-C" becomes "USB" + "C".
   Is a single-letter token "C" useful for search?
2. If you remove apostrophes, "L'Oreal" becomes "LOreal" — will that
   match a search for "Loreal"? (Depends on lowercasing order)
3. You might want different strategies for different separators
4. Python's `re.sub()` can handle all of these in one or two lines

## What to build

Decide on a strategy for each separator type. Implement it in
`normalize_text` before the whitespace split. Test with the edge-case
texts in `conftest.py` to verify your choices.
