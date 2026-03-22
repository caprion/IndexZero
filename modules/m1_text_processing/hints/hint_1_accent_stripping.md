# Hint 1: Accent stripping

## The problem

Characters like e and e with an accent look the same to a human reading
a product title, but your tokenizer sees them as different bytes. If one
product says "cafe" and another says "cafe" with an accent, they won't
match during search.

## The concept

Unicode has two ways to represent "e with accent":
- As a single character (precomposed)
- As two characters: the letter "e" + a combining accent mark (decomposed)

Python's `unicodedata` module can convert between these forms. The
decomposed form (NFD) separates the base letter from the accent mark.
Accent marks have a Unicode category of "Mn" (Mark, nonspacing).

## What to explore

1. `unicodedata.normalize()` — look at the "NFD" form
2. `unicodedata.category()` — check what category each character has
3. Try it in a Python REPL:
   ```
   import unicodedata
   text = "caf\u0065\u0301"  # cafe with combining accent
   for c in unicodedata.normalize('NFD', text):
       print(repr(c), unicodedata.category(c))
   ```
4. Characters you want to keep have categories starting with "L" (letter)
   or "N" (number). The ones you want to strip are "Mn".

## What to build

A loop or comprehension that decomposes the text, filters out combining
marks, and returns the cleaned string.
