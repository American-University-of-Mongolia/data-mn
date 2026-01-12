"""
Pytest configuration and fixtures for data.mn validation tests.
"""

import pytest
from pathlib import Path
import yaml

# Base paths
TOOLS_DIR = Path(__file__).parent.parent
DATA_MN_DIR = TOOLS_DIR.parent / "data.mn"
FIXTURES_DIR = Path(__file__).parent / "fixtures"

# Known-good datasets (existing production data)
GOOD_DATASETS = [
    "gdp-nominal",
    "gdp-real",
    "gdp-growth-rate",
    "population-total",
    "cpi-monthly-ulaanbaatar",
]


def parse_frontmatter(mdx_path: Path) -> dict:
    """Extract YAML frontmatter from MDX file."""
    if not mdx_path.exists():
        return {}
    content = mdx_path.read_text(encoding='utf-8')
    if not content.startswith('---'):
        return {}
    lines = content.split('\n')
    try:
        end_idx = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == '---')
        return yaml.safe_load('\n'.join(lines[1:end_idx])) or {}
    except (StopIteration, yaml.YAMLError):
        return {}


def get_mdx_body(mdx_path: Path) -> str:
    """Extract body content (after frontmatter) from MDX file."""
    if not mdx_path.exists():
        return ""
    content = mdx_path.read_text(encoding='utf-8')
    if not content.startswith('---'):
        return content
    lines = content.split('\n')
    try:
        end_idx = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == '---')
        return '\n'.join(lines[end_idx + 1:])
    except StopIteration:
        return ""


@pytest.fixture
def good_mdx_en():
    """Returns path to a known-good English MDX file."""
    return DATA_MN_DIR / "src/data/data/en/gdp-nominal.mdx"


@pytest.fixture
def good_mdx_mn():
    """Returns path to a known-good Mongolian MDX file."""
    return DATA_MN_DIR / "src/data/data/mn/gdp-nominal.mdx"


@pytest.fixture
def good_csv_en():
    """Returns path to a known-good English CSV file."""
    return DATA_MN_DIR / "public/datasets/gdp-nominal-en.csv"


@pytest.fixture
def good_csv_mn():
    """Returns path to a known-good Mongolian CSV file."""
    return DATA_MN_DIR / "public/datasets/gdp-nominal-mn.csv"


@pytest.fixture
def good_chart_en():
    """Returns path to a known-good English chart spec."""
    return DATA_MN_DIR / "public/charts/gdp-nominal-en.json"


@pytest.fixture
def good_chart_mn():
    """Returns path to a known-good Mongolian chart spec."""
    return DATA_MN_DIR / "public/charts/gdp-nominal-mn.json"


@pytest.fixture
def all_good_datasets():
    """Returns list of all known-good dataset IDs."""
    return GOOD_DATASETS
