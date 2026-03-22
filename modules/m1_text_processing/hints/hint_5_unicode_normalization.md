# Hint 5: Unicode normalization (NFKC)

## The problem

The same text can be stored differently in Unicode. The trademark
symbol "TM" has a single-character form (one codepoint) and a
two-letter form ("T" + "M"). Ligatures like "fi" (one character)
look identical to "f" + "i" (two characters). If your tokenizer
doesn't normalize these, identical-looking text produces different
tokens.

## The concept

Unicode defines four normalization forms. The one you want is NFKC:
- **K** = compatibility decomposition (breaks "TM" symbol into "T"+"M",
  "fi" ligature into "f"+"i")
- **C** = canonical composition (recombines where possible, keeping
  things clean)

This should be your FIRST normalization step — before lowercasing,
before accent stripping, before anything else. It gives you a
consistent starting point.

## What to explore

1. Python's `unicodedata` module has a `normalize()` function
2. Try in a REPL:
   ```
   import unicodedata
   # The fi ligature (single character):
   print(len("\ufb01"))           # 1
   print(len(unicodedata.normalize("NFKC", "\ufb01")))  # 2
   ```
3. The trademark symbol:
   ```
   print(unicodedata.normalize("NFKC", "\u2122"))  # "TM"
   ```

## What to build

One line at the top of `normalize_text` that passes the input through
NFKC normalization before any other processing.
