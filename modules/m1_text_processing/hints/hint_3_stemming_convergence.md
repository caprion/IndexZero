# Hint 3: Stemming convergence

## The problem

Your stemmer strips "-ing" from "running" and gets "runn". It strips
"-s" from "runs" and gets "run". Those don't match — but they should,
because they're forms of the same word.

## The concept

When English adds "-ing" to a short verb, it doubles the final
consonant: run → running, stop → stopping, hit → hitting. A suffix
stripper that removes "-ing" leaves the doubled consonant behind.

The fix: after stripping any suffix, check whether the last two
characters are the same consonant. If so, remove one.

## What to explore

1. Strip "-ing" from "running" — what do you get?
2. Are the last two characters of that result identical?
3. What about "stopping" → ? and "hitting" → ?
4. Does this rule break anything? Try "sing" → strip "-ing" → "s"
   (too short — you need a minimum length guard)
5. The same doubling happens with "-ed" (stopped) and "-er" (runner)

## What to build

After your if/elif chain strips a suffix, add one more check: if the
stem ends with a repeated consonant and the stem is long enough,
drop one copy.
