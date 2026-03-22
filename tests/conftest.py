"""Shared test fixtures for IndexZero.

These fixtures are automatically discovered by pytest. They provide
consistent sample data for all test modules.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from indexzero.text_processing import TokenizerConfig


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

@pytest.fixture
def tiny_csv_path() -> Path:
    """Path to the tiny Flipkart titles CSV (8 rows, for unit tests)."""
    return Path(__file__).resolve().parent.parent / "data" / "flipkart_titles_tiny.csv"


# ---------------------------------------------------------------------------
# Sample texts — realistic product titles from Indian e-commerce
# ---------------------------------------------------------------------------

SAMPLE_TEXTS: list[str] = [
    "Redmi Note 13 5G Mobile Phone 8GB RAM 256GB Storage",
    "Samsung Galaxy M14 5G 6GB RAM 128GB Dark Blue",
    "Nike Revolution Running Shoes for Men",
    "Women Cotton Kurti with Dupatta Set Maroon",
    "Boat Airdopes 141 Bluetooth Earbuds with Mic",
    "Milton Thermosteel Bottle 1 Litre Silver",
    "HP 15s Ryzen 5 Laptop 16GB RAM 512GB SSD",
    "Pigeon Non Stick Tawa 28 cm Black",
]

# Edge-case texts that stress separators, apostrophes, and mixed scripts.
# These expose shallow implementations that only handle ASCII alphanumeric.
EDGE_TEXTS: list[str] = [
    "3-in-1 USB-C Cable Type-C to Lightning/Micro-USB",
    "L'Oreal Paris Revitalift Creme Anti-Wrinkle",
    "women's non-stick tawa 24cm/28cm combo",
    "boAt Rockerz 450 Pro++ ANC Headphone",
    "Bajaj 750W/1000W Mixer Grinder (3 Jars)",
]


@pytest.fixture
def sample_texts() -> list[str]:
    """A list of 8 realistic product titles."""
    return list(SAMPLE_TEXTS)


@pytest.fixture
def edge_texts() -> list[str]:
    """Texts with hyphens, apostrophes, slashes, and mixed punctuation."""
    return list(EDGE_TEXTS)


@pytest.fixture
def all_texts() -> list[str]:
    """All sample + edge texts combined."""
    return list(SAMPLE_TEXTS) + list(EDGE_TEXTS)


@pytest.fixture
def sample_text() -> str:
    """A single product title for quick tests."""
    return SAMPLE_TEXTS[0]


# ---------------------------------------------------------------------------
# Configs
# ---------------------------------------------------------------------------

@pytest.fixture
def default_config() -> TokenizerConfig:
    """Default tokenizer config (lowercase on, everything else off)."""
    return TokenizerConfig()


@pytest.fixture
def full_config() -> TokenizerConfig:
    """Config with all optional processing enabled."""
    return TokenizerConfig(
        lowercase=True,
        strip_accents=True,
        split_numeric_boundaries=True,
        drop_stopwords=True,
        stemming="suffix",
    )


@pytest.fixture
def no_lowercase_config() -> TokenizerConfig:
    """Config with lowercasing disabled."""
    return TokenizerConfig(lowercase=False)
