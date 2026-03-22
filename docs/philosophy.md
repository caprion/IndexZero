# M1 Design Philosophy

How M1 was designed and why. Use this as a reference when building M2 and beyond.

## The core bet

Every normalization choice creates downstream consequences. M1 exists to make students discover this by building a tokenizer, not by reading about tokenizers.

The module doesn't ask "what is the best tokenizer." It asks "what happens when you change this one flag." Students who finish M1 can defend their choices with numbers and articulate what would break if they changed their mind.

## Skeleton-first, not lecture-first

Students start with a working repo and failing tests. The tests define what "done" looks like before any code is written. The README is a workshop guide, not a textbook chapter.

This means the README has to be precise about prerequisites. If the student needs to know what a dataclass is, the README explains it in three lines with one code example. No links to external tutorials. No "you should already know this."

## Three tiers of help

1. **Docstrings** say WHAT each function should do. No code snippets, no algorithm names.
2. **The README** explains WHY each processing step matters for search. Stemming collapses vocabulary, but aggressive stemming merges words that should stay separate.
3. **The hints/ folder** explains HOW to implement the hard parts. Concept first, then which Python module to explore, then a REPL experiment. Still no copy-paste implementation.

Weak students open the hints. Strong students don't. AI finds the hints too, but the decision log tracks which ones you opened and what you tried before opening them. That's the signal.

## Assessment measures understanding, not code

Four artifacts, each testing a different thing:

- **Decision log** forces students to describe what went wrong before they got to their current solution. "I added lowercasing" is weak. "Lowercasing merged HP-the-brand and hp-the-motor, vocabulary dropped from 847 to 612, I'm keeping it because the reduction is worth the ambiguity" is strong.
- **Break-it** forces students to attack their own code. Finding inputs that break your tokenizer requires understanding what the tokenizer actually does.
- **Consequence chain** asks students to predict what happens in M3 if they change their M1 config. They write predictions before M3 exists. When they reach M3, they compare.
- **Config mutations** ask students to predict which tests fail when they flip one flag. The point is building a mental model of config interactions.

AI can generate code for all four. AI cannot generate the "what went wrong first" narrative without having actually hit the bug. That's the design constraint.

## Invariant tests, not exact-output tests

Tests check rules, not specific strings:

- Token count equals sum of term counts
- No empty tokens
- Same input + same config = same output
- Document frequency never exceeds document count

This means there's no single "correct" tokenizer. Students can make different design choices and still pass all tests. The decision log captures why their choices differ.

## Config flags are the experiment knobs

`TokenizerConfig` has flags for lowercasing, stopwords, stemming, numeric splitting, accent stripping. The CLI exposes all of them. Students run the same input with different flags and compare output.

This is how the observe prompts work. "Run with `--drop-stopwords`, record vocabulary size. Run without, record again. Which had a bigger effect?" The CLI turns configuration into a measurable experiment.

## One codebase grows

M2 imports M1's `TokenizedDocument` and `Vocabulary` directly. If M1 output is inconsistent, M2 becomes a cleanup module. This is by design. Students feel the consequence of their M1 choices when they reach M2.

The interface contract (`interface_contract.md`) documents exactly what M2 can rely on. Students read it during M1 so they know what's at stake.

## Python only

Supporting multiple languages breaks the "one codebase that grows" model. If M1 is in Rust and M2 is in Python, M2 can't import M1's vocabulary. File-based serialization would work, but it replaces search concepts with file I/O debugging.

Every comparable course picked one language and stuck with it. Python is the choice because the focus is search, not language mechanics.

## What carries forward to M2+

- **Skeleton + failing tests on day one.** Students know what "done" looks like before writing code.
- **Three-tier help.** Docstrings = WHAT. README = WHY. Hints = HOW.
- **Assessment artifacts that test understanding, not typing.** Decision logs, break-it, consequence chains.
- **CLI as experiment tool.** Config flags as knobs, stdout as measurement.
- **Invariant tests.** Multiple valid implementations, rules that must hold regardless.
- **Interface contracts.** Each module documents what the next module depends on.
