# Hint 2: Numeric boundary splitting

## The problem

Product titles glue numbers to units: "8GB", "512GB", "750W", "28cm".
If someone searches for "8" or "GB" separately, your tokenizer needs
to have split them. But "Note13Pro" should also split into parts.

## The concept

The boundary between a digit and a letter (or letter and digit) is
where you need to insert a space. This is a pattern replacement problem.

## What to explore

1. Python's `re.sub()` can find a pattern and replace it with something
2. Capture groups `(\d)` and `([a-zA-Z])` let you match "digit followed
   by letter" and keep both parts
3. The replacement string can reference captured groups with `\1`, `\2`
4. Try in a REPL:
   ```
   import re
   text = "8GB RAM 512GB SSD"
   # What pattern matches "a digit immediately followed by a letter"?
   # What should the replacement be?
   ```
5. You need two passes: digit→letter AND letter→digit (for "Note13Pro")

## What to build

Two `re.sub()` calls — one for each boundary direction. The replacement
inserts a space between the captured groups.
