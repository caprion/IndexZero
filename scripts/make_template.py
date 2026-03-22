#!/usr/bin/env python3
"""Generate a student-facing template from the instructor repository.

Purpose
-------
``make_template.py`` reads the working source tree and produces a clean
student starter by replacing function bodies in ``tokenizer.py`` and
``vocabulary.py`` with ``raise NotImplementedError("Students implement
this in M1.")``, while keeping contracts, imports, docstrings, and tests
intact.

The resulting tree can be pushed as a GitHub Classroom template or a
public fork-me repository.

Usage (planned)
---------------
::

    python scripts/make_template.py --src src/indexzero/text_processing \\
                                    --out  dist/template/src/indexzero/text_processing

How it works (planned)
----------------------
1. Copy the entire repo tree to *out*, excluding ``_reference_*`` files,
   ``__pycache__``, ``.venv``, and build artefacts.
2. For each ``.py`` file listed in a ``TEMPLATE_TARGETS`` manifest:
   a. Parse the AST.
   b. For every function whose body is *not* a bare ``raise
      NotImplementedError``, replace the body with the stub docstring +
      ``raise NotImplementedError``.
   c. Write the modified source back.
3. Validate that ``pytest tests/`` fails with ``NotImplementedError`` on
   every student function and passes on all other tests.

TODO
----
- [ ] Implement AST-based body replacement
- [ ] Add --validate flag that runs pytest on the output
- [ ] Add --manifest flag that lists which files/functions to stub
- [ ] Handle edge cases: decorators, class methods, nested functions
"""

from __future__ import annotations


def main() -> None:
    raise NotImplementedError(
        "make_template.py is a planned tool.  See the module docstring for design notes."
    )


if __name__ == "__main__":
    main()
