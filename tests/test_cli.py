"""Tests for the CLI entry point.

These tests verify that the CLI can at least be invoked. They will
produce useful errors once the tokenizer is implemented.

Run:  pytest tests/test_cli.py -v
"""

from __future__ import annotations

import subprocess
import sys

import pytest


class TestCLI:
    """Smoke tests for `python -m indexzero`."""

    def test_help_exits_cleanly(self) -> None:
        """The --help flag should work even before implementation."""
        result = subprocess.run(
            [sys.executable, "-m", "indexzero", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "indexzero" in result.stdout.lower()

    def test_tokenize_help(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "indexzero", "tokenize", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_vocab_help(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "indexzero", "vocab", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
