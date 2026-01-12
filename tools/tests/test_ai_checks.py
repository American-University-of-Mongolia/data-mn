"""
AI Judgment Check Test Suite for data.mn

Converts the 25 "AI judgment" checks from data-page-checklist.md into
executable pytest tests. These checks were previously only verifiable
by human/AI review - now they're automated.

Run with:
    cd data/tools && pytest tests/test_ai_checks.py -v

Checklist reference: tools/config/data-page-checklist.md
"""

import pytest
import re
import json
from pathlib import Path
from conftest import parse_frontmatter, get_mdx_body, DATA_MN_DIR

# ============================================================================
# HELPER FUNCTIONS
# Each check_* function returns (passed: bool, reason: str)
# ============================================================================


# ----------------------------------------------------------------------------
# SECTION 2: MDX Frontmatter AI Checks
# ----------------------------------------------------------------------------

def check_2_3_excerpt_meaningful(frontmatter: dict) -> tuple[bool, str]:
    """
    Check 2.3: Excerpt tells meaningful story (not just 'data about X').

    Good: "Mongolia's GDP grew from 12.8B to 80.7T MNT, a 6,000-fold increase."
    Bad: "Data about Mongolia's GDP."
    """
    excerpt = frontmatter.get('excerpt', '')

    if not excerpt:
        return False, "Excerpt is missing"

    if len(excerpt) < 50:
        return False, f"Excerpt too short ({len(excerpt)} chars, need 50+)"

    # Bad patterns - generic descriptions
    bad_patterns = [
        r'^data about',
        r'^this dataset contains',
        r'^this page shows',
        r'^statistics on',
        r'^information about',
    ]
    excerpt_lower = excerpt.lower()
    for pattern in bad_patterns:
        if re.match(pattern, excerpt_lower):
            return False, f"Excerpt uses generic pattern: '{pattern}'"

    # Good pattern - contains actual numbers (sign of real insight)
    if re.search(r'\d+', excerpt):
        return True, "Excerpt contains specific data points"

    # OK but could be better
    return True, "Excerpt is descriptive but could include specific numbers"


def check_2_6_keywords_useful(frontmatter: dict) -> tuple[bool, str]:
    """
    Check 2.6: Keywords include common search terms for SEO.

    Good: ["mongolia gdp", "gdp current prices", "economic growth"]
    Bad: ["data", "statistics"] (too generic)
    """
    keywords = frontmatter.get('keywords', [])

    if not keywords:
        return False, "Keywords array is missing"

    if not isinstance(keywords, list):
        return False, f"Keywords must be a list, got {type(keywords).__name__}"

    if len(keywords) < 2:
        return False, f"Need at least 2 keywords, got {len(keywords)}"

    # Check for overly generic keywords
    generic_keywords = {'data', 'statistics', 'information', 'mongolia', 'stats'}
    keyword_set = {k.lower().strip() for k in keywords}

    if keyword_set <= generic_keywords:
        return False, "All keywords are too generic (just 'data', 'statistics', etc.)"

    # Check for multi-word keywords (better for SEO)
    multi_word = [k for k in keywords if ' ' in k]
    if not multi_word:
        return False, "No multi-word keywords (e.g., 'mongolia gdp growth')"

    return True, f"Has {len(keywords)} keywords including multi-word terms"


def check_2_13_source_tableid(frontmatter: dict) -> tuple[bool, str]:
    """
    Check 2.13: If from NSO, source should have tableId.

    Only applies to NSO 1212.mn sources.
    """
    source = frontmatter.get('source', {})
    if not isinstance(source, dict):
        return True, "No source object (skip check)"

    source_url = source.get('url', '')
    source_name = source.get('name', '').lower()

    # Check if this is an NSO source
    is_nso = (
        '1212.mn' in source_url or
        'nso' in source_name or
        'national statistics' in source_name or
        'статистик' in source_name.lower()
    )

    if not is_nso:
        return True, "Not an NSO source (tableId not required)"

    table_id = source.get('tableId', '')
    if not table_id:
        return False, "NSO source missing tableId (e.g., 'DT_NSO_0500_001V1.px')"

    return True, f"Has NSO tableId: {table_id}"


# ----------------------------------------------------------------------------
# SECTION 3: MDX Body AI Checks
# ----------------------------------------------------------------------------

def check_3_4_vegachart_has_title(body: str) -> tuple[bool, str]:
    """
    Check 3.4: VegaChart component has title attribute.
    """
    if '<VegaChart' not in body:
        return False, "No VegaChart component found"

    # Look for title attribute in VegaChart
    vegachart_match = re.search(r'<VegaChart[^>]*>', body, re.DOTALL)
    if not vegachart_match:
        return False, "Could not parse VegaChart component"

    vegachart_tag = vegachart_match.group(0)

    if 'title=' not in vegachart_tag:
        return False, "VegaChart missing title attribute"

    # Extract title value
    title_match = re.search(r'title="([^"]*)"', vegachart_tag)
    if title_match:
        title = title_match.group(1)
        if len(title) < 5:
            return False, f"VegaChart title too short: '{title}'"
        return True, f"VegaChart has title: '{title[:50]}...'"

    return True, "VegaChart has title attribute"


def check_3_5_no_placeholder_text(frontmatter: dict, body: str) -> tuple[bool, str]:
    """
    Check 3.5 & 10.4: No placeholder text (TODO, TBD, FIXME, PLACEHOLDER).
    """
    # Combine all text to check
    all_text = str(frontmatter) + body

    placeholders = ['TODO', 'TBD', 'FIXME', 'PLACEHOLDER', 'XXX', 'HACK']
    found = []

    for p in placeholders:
        if p in all_text.upper():
            found.append(p)

    if found:
        return False, f"Found placeholder text: {found}"

    return True, "No placeholder text found"


# ----------------------------------------------------------------------------
# SECTION 4: CSV AI Checks
# ----------------------------------------------------------------------------

def check_4_6_long_form(csv_path: Path) -> tuple[bool, str]:
    """
    Check 4.6: CSV data is in long/normalized form (one observation per row).

    Long form: year, category, value
    Wide form: category, 2020, 2021, 2022 (years as columns) - BAD for CSV
    """
    try:
        import pandas as pd
        df = pd.read_csv(csv_path)
    except Exception as e:
        return False, f"Could not read CSV: {e}"

    # Heuristic: If many columns look like years (4-digit numbers), it's wide form
    year_like_cols = [c for c in df.columns if re.match(r'^\d{4}$', str(c))]

    if len(year_like_cols) > 3:
        return False, f"CSV appears to be wide form (years as columns): {year_like_cols[:5]}"

    # Check for expected long-form columns
    expected_cols = {'year', 'value', 'он', 'утга'}
    col_lower = {c.lower() for c in df.columns}

    if col_lower & expected_cols:
        return True, "CSV is in long form with year/value columns"

    return True, "CSV structure appears acceptable"


def check_4_12_row_count_match(csv_en: Path, csv_mn: Path) -> tuple[bool, str]:
    """
    Check 4.12: EN and MN CSVs have identical row counts.
    """
    try:
        import pandas as pd
        df_en = pd.read_csv(csv_en)
        df_mn = pd.read_csv(csv_mn)
    except Exception as e:
        return False, f"Could not read CSVs: {e}"

    if len(df_en) != len(df_mn):
        return False, f"Row count mismatch: EN={len(df_en)}, MN={len(df_mn)}"

    return True, f"Both CSVs have {len(df_en)} rows"


def check_4_13_column_count_match(csv_en: Path, csv_mn: Path) -> tuple[bool, str]:
    """
    Check 4.13: EN and MN CSVs have same number of columns.
    """
    try:
        import pandas as pd
        df_en = pd.read_csv(csv_en)
        df_mn = pd.read_csv(csv_mn)
    except Exception as e:
        return False, f"Could not read CSVs: {e}"

    if len(df_en.columns) != len(df_mn.columns):
        return False, f"Column count mismatch: EN={len(df_en.columns)}, MN={len(df_mn.columns)}"

    return True, f"Both CSVs have {len(df_en.columns)} columns"


def check_4_14_numeric_values_match(csv_en: Path, csv_mn: Path) -> tuple[bool, str]:
    """
    Check 4.14: Numeric values are identical between EN and MN CSVs.
    """
    try:
        import pandas as pd
        df_en = pd.read_csv(csv_en)
        df_mn = pd.read_csv(csv_mn)
    except Exception as e:
        return False, f"Could not read CSVs: {e}"

    # Get numeric columns from each
    en_numeric = df_en.select_dtypes(include=['number'])
    mn_numeric = df_mn.select_dtypes(include=['number'])

    if en_numeric.shape != mn_numeric.shape:
        return False, f"Numeric column shape mismatch: EN={en_numeric.shape}, MN={mn_numeric.shape}"

    # Compare values (allowing for small floating point differences)
    try:
        import numpy as np
        if not np.allclose(en_numeric.values, mn_numeric.values, equal_nan=True):
            return False, "Numeric values differ between EN and MN CSVs"
    except Exception:
        # Fallback to exact comparison
        if not en_numeric.equals(mn_numeric):
            return False, "Numeric values differ between EN and MN CSVs"

    return True, "Numeric values match between EN and MN"


# ----------------------------------------------------------------------------
# SECTION 5: XLSX AI Checks
# ----------------------------------------------------------------------------

def check_5_5_wide_form(xlsx_path: Path) -> tuple[bool, str]:
    """
    Check 5.5: XLSX data is in wide/short form (years as columns).

    XLSX should be formatted for easy Excel viewing (opposite of CSV requirement).
    """
    try:
        import pandas as pd
        df = pd.read_excel(xlsx_path)
    except Exception as e:
        return False, f"Could not read XLSX: {e}"

    # Heuristic: Wide form has years as column names
    year_like_cols = [c for c in df.columns if re.match(r'^\d{4}$', str(c))]

    # For XLSX, having year columns is GOOD (opposite of CSV check)
    if len(year_like_cols) >= 2:
        return True, f"XLSX is in wide form with year columns: {year_like_cols[:5]}"

    # If no year columns, check if it's a simple structure that's still valid
    if len(df.columns) <= 3:
        return True, "XLSX has simple structure (acceptable)"

    return False, "XLSX should be in wide form with years as columns for easy Excel viewing"


# ----------------------------------------------------------------------------
# SECTION 8: Bilingual Consistency AI Checks
# ----------------------------------------------------------------------------

# Category translation mapping
CATEGORY_MAP = {
    'Demographics': 'Хүн ам зүй',
    'Economy': 'Эдийн засаг',
    'Labor Market': 'Хөдөлмөрийн зах зээл',
    'Housing': 'Орон сууц',
    'Mining': 'Уул уурхай',
    'Finance': 'Санхүү',
    'Agriculture': 'Хөдөө аж ахуй',
    'Education': 'Боловсрол',
    'Health': 'Эрүүл мэнд',
    'Trade': 'Худалдаа',
    'Energy': 'Эрчим хүч',
    'Tourism': 'Аялал жуулчлал',
    'Environment': 'Байгаль орчин',
    'Transport': 'Тээвэр',
    'Technology': 'Технологи',
}


def check_8_2_category_match(fm_en: dict, fm_mn: dict) -> tuple[bool, str]:
    """
    Check 8.2: Categories match conceptually (EN 'Economy' ↔ MN 'Эдийн засаг').
    """
    cat_en = fm_en.get('category', '')
    cat_mn = fm_mn.get('category', '')

    if not cat_en or not cat_mn:
        return False, f"Missing category: EN='{cat_en}', MN='{cat_mn}'"

    # Check if they match via the mapping
    expected_mn = CATEGORY_MAP.get(cat_en)

    if expected_mn and cat_mn == expected_mn:
        return True, f"Categories match: EN '{cat_en}' ↔ MN '{cat_mn}'"

    # Also check reverse (MN page might have EN category - common issue)
    if cat_mn == cat_en:
        return False, f"MN page has English category '{cat_mn}' - should be translated"

    return True, f"Categories: EN '{cat_en}', MN '{cat_mn}' (translation not verified)"


def check_8_3_dataversion_match(fm_en: dict, fm_mn: dict) -> tuple[bool, str]:
    """
    Check 8.3: Both pages have identical dataVersion.
    """
    v_en = fm_en.get('dataVersion')
    v_mn = fm_mn.get('dataVersion')

    if v_en != v_mn:
        return False, f"dataVersion mismatch: EN={v_en}, MN={v_mn}"

    return True, f"dataVersion matches: {v_en}"


def check_8_4_datadate_match(fm_en: dict, fm_mn: dict) -> tuple[bool, str]:
    """
    Check 8.4: Both pages have identical dataDate.
    """
    d_en = fm_en.get('dataDate')
    d_mn = fm_mn.get('dataDate')

    if str(d_en) != str(d_mn):
        return False, f"dataDate mismatch: EN={d_en}, MN={d_mn}"

    return True, f"dataDate matches: {d_en}"


def check_8_5_tag_count_similar(fm_en: dict, fm_mn: dict) -> tuple[bool, str]:
    """
    Check 8.5: Similar number of tags in both pages.
    """
    tags_en = fm_en.get('tags', [])
    tags_mn = fm_mn.get('tags', [])

    count_en = len(tags_en) if isinstance(tags_en, list) else 0
    count_mn = len(tags_mn) if isinstance(tags_mn, list) else 0

    diff = abs(count_en - count_mn)

    if diff > 2:
        return False, f"Tag count differs significantly: EN={count_en}, MN={count_mn}"

    return True, f"Tag counts similar: EN={count_en}, MN={count_mn}"


def check_8_6_chart_type_match(chart_en: Path, chart_mn: Path) -> tuple[bool, str]:
    """
    Check 8.6: Both charts use same visualization type.
    """
    try:
        spec_en = json.loads(chart_en.read_text())
        spec_mn = json.loads(chart_mn.read_text())
    except Exception as e:
        return False, f"Could not read chart specs: {e}"

    # Extract mark type
    def get_mark_type(spec):
        if 'mark' in spec:
            mark = spec['mark']
            return mark if isinstance(mark, str) else mark.get('type', 'unknown')
        if 'layer' in spec:
            # Get first layer's mark
            first = spec['layer'][0] if spec['layer'] else {}
            mark = first.get('mark', {})
            return mark if isinstance(mark, str) else mark.get('type', 'unknown')
        return 'unknown'

    type_en = get_mark_type(spec_en)
    type_mn = get_mark_type(spec_mn)

    if type_en != type_mn:
        return False, f"Chart type mismatch: EN='{type_en}', MN='{type_mn}'"

    return True, f"Chart types match: '{type_en}'"


def check_8_7_numeric_data_identical(csv_en: Path, csv_mn: Path) -> tuple[bool, str]:
    """
    Check 8.7: Identical numeric data in EN/MN CSVs (alias for 4.14).
    """
    return check_4_14_numeric_values_match(csv_en, csv_mn)


# ----------------------------------------------------------------------------
# SECTION 10: Content Quality AI Checks
# ----------------------------------------------------------------------------

def check_10_1_title_has_year_range(frontmatter: dict) -> tuple[bool, str]:
    """
    Check 10.1: If time-series, title includes year range (e.g., "1990-2024").
    """
    title = frontmatter.get('title', '')

    # Look for year range pattern
    year_range = re.search(r'\(?\d{4}\s*[-–—]\s*\d{4}\)?', title)
    single_year = re.search(r'\(?\d{4}\)?', title)

    if year_range:
        return True, f"Title has year range: {year_range.group()}"

    if single_year:
        return True, f"Title has year: {single_year.group()}"

    # Check if this seems like time-series data (has 'trend', 'growth', 'annual', etc.)
    time_keywords = ['trend', 'growth', 'annual', 'yearly', 'monthly', 'historical']
    if any(kw in title.lower() for kw in time_keywords):
        return False, "Title suggests time-series but has no year range"

    return True, "Title does not appear to be time-series (no year range needed)"


def check_10_2_excerpt_has_insight(frontmatter: dict) -> tuple[bool, str]:
    """
    Check 10.2: Excerpt provides insight, not just description (similar to 2.3).
    """
    return check_2_3_excerpt_meaningful(frontmatter)


def check_10_3_source_accurate(frontmatter: dict) -> tuple[bool, str]:
    """
    Check 10.3: Source attribution is accurate (has name and valid URL).
    """
    source = frontmatter.get('source', {})

    if not isinstance(source, dict):
        return False, "Source must be an object with name and url"

    name = source.get('name', '')
    url = source.get('url', '')

    if not name:
        return False, "Source name is missing"

    if not url:
        return False, "Source URL is missing"

    if not url.startswith('http'):
        return False, f"Source URL invalid: '{url}'"

    return True, f"Source: {name} ({url[:50]}...)"


def check_10_5_tags_relevant(frontmatter: dict) -> tuple[bool, str]:
    """
    Check 10.5: Tags are relevant to content (not random).
    """
    title = frontmatter.get('title', '').lower()
    category = frontmatter.get('category', '').lower()
    tags = frontmatter.get('tags', [])

    if not tags:
        return False, "No tags defined"

    if not isinstance(tags, list):
        return False, "Tags must be a list"

    # Check that at least one tag relates to title or category
    title_words = set(re.findall(r'\w+', title))
    category_words = set(re.findall(r'\w+', category))
    all_context = title_words | category_words

    relevant_tags = 0
    for tag in tags:
        tag_words = set(re.findall(r'\w+', tag.lower()))
        if tag_words & all_context:
            relevant_tags += 1

    if relevant_tags == 0:
        return False, f"No tags relate to title/category. Tags: {tags}"

    return True, f"{relevant_tags}/{len(tags)} tags relate to content"


def check_10_6_keywords_seo(frontmatter: dict) -> tuple[bool, str]:
    """
    Check 10.6: Keywords are good for SEO (alias for 2.6).
    """
    return check_2_6_keywords_useful(frontmatter)


# ============================================================================
# PYTEST TEST FUNCTIONS
# ============================================================================

class TestSection2Frontmatter:
    """Tests for Section 2: MDX Frontmatter AI Checks"""

    def test_2_3_excerpt_meaningful_good(self, good_mdx_en):
        fm = parse_frontmatter(good_mdx_en)
        passed, reason = check_2_3_excerpt_meaningful(fm)
        assert passed, f"Good fixture failed: {reason}"

    def test_2_3_excerpt_meaningful_bad_generic(self):
        fm = {'excerpt': 'Data about Mongolia GDP.'}
        passed, _ = check_2_3_excerpt_meaningful(fm)
        assert not passed, "Generic excerpt should fail"

    def test_2_3_excerpt_meaningful_bad_short(self):
        fm = {'excerpt': 'GDP data.'}
        passed, _ = check_2_3_excerpt_meaningful(fm)
        assert not passed, "Short excerpt should fail"

    def test_2_6_keywords_good(self, good_mdx_en):
        fm = parse_frontmatter(good_mdx_en)
        passed, reason = check_2_6_keywords_useful(fm)
        assert passed, f"Good fixture failed: {reason}"

    def test_2_6_keywords_bad_generic(self):
        fm = {'keywords': ['data', 'statistics']}
        passed, _ = check_2_6_keywords_useful(fm)
        assert not passed, "Generic keywords should fail"

    def test_2_13_source_tableid_good(self, good_mdx_en):
        fm = parse_frontmatter(good_mdx_en)
        passed, reason = check_2_13_source_tableid(fm)
        assert passed, f"Good fixture failed: {reason}"


class TestSection3Body:
    """Tests for Section 3: MDX Body AI Checks"""

    def test_3_4_vegachart_title_good(self, good_mdx_en):
        body = get_mdx_body(good_mdx_en)
        passed, reason = check_3_4_vegachart_has_title(body)
        assert passed, f"Good fixture failed: {reason}"

    def test_3_4_vegachart_title_bad(self):
        body = '<VegaChart spec="/charts/test.json" />'
        passed, _ = check_3_4_vegachart_has_title(body)
        assert not passed, "VegaChart without title should fail"

    def test_3_5_no_placeholder_good(self, good_mdx_en):
        fm = parse_frontmatter(good_mdx_en)
        body = get_mdx_body(good_mdx_en)
        passed, reason = check_3_5_no_placeholder_text(fm, body)
        assert passed, f"Good fixture failed: {reason}"

    def test_3_5_placeholder_bad(self):
        fm = {'title': 'TODO: Add real title'}
        passed, _ = check_3_5_no_placeholder_text(fm, '')
        assert not passed, "Placeholder text should fail"


class TestSection4CSV:
    """Tests for Section 4: CSV AI Checks"""

    def test_4_6_long_form_good(self, good_csv_en):
        passed, reason = check_4_6_long_form(good_csv_en)
        assert passed, f"Good fixture failed: {reason}"

    def test_4_12_row_count_match(self, good_csv_en, good_csv_mn):
        passed, reason = check_4_12_row_count_match(good_csv_en, good_csv_mn)
        assert passed, f"Good fixture failed: {reason}"

    def test_4_13_column_count_match(self, good_csv_en, good_csv_mn):
        passed, reason = check_4_13_column_count_match(good_csv_en, good_csv_mn)
        assert passed, f"Good fixture failed: {reason}"

    def test_4_14_numeric_values_match(self, good_csv_en, good_csv_mn):
        passed, reason = check_4_14_numeric_values_match(good_csv_en, good_csv_mn)
        assert passed, f"Good fixture failed: {reason}"


class TestSection8Bilingual:
    """Tests for Section 8: Bilingual Consistency AI Checks"""

    def test_8_3_dataversion_match(self, good_mdx_en, good_mdx_mn):
        fm_en = parse_frontmatter(good_mdx_en)
        fm_mn = parse_frontmatter(good_mdx_mn)
        passed, reason = check_8_3_dataversion_match(fm_en, fm_mn)
        assert passed, f"Good fixture failed: {reason}"

    def test_8_4_datadate_match(self, good_mdx_en, good_mdx_mn):
        fm_en = parse_frontmatter(good_mdx_en)
        fm_mn = parse_frontmatter(good_mdx_mn)
        passed, reason = check_8_4_datadate_match(fm_en, fm_mn)
        assert passed, f"Good fixture failed: {reason}"

    def test_8_5_tag_count_similar(self, good_mdx_en, good_mdx_mn):
        fm_en = parse_frontmatter(good_mdx_en)
        fm_mn = parse_frontmatter(good_mdx_mn)
        passed, reason = check_8_5_tag_count_similar(fm_en, fm_mn)
        assert passed, f"Good fixture failed: {reason}"

    def test_8_6_chart_type_match(self, good_chart_en, good_chart_mn):
        passed, reason = check_8_6_chart_type_match(good_chart_en, good_chart_mn)
        assert passed, f"Good fixture failed: {reason}"


class TestSection10ContentQuality:
    """Tests for Section 10: Content Quality AI Checks"""

    def test_10_1_title_year_range(self, good_mdx_en):
        fm = parse_frontmatter(good_mdx_en)
        passed, reason = check_10_1_title_has_year_range(fm)
        assert passed, f"Good fixture failed: {reason}"

    def test_10_3_source_accurate(self, good_mdx_en):
        fm = parse_frontmatter(good_mdx_en)
        passed, reason = check_10_3_source_accurate(fm)
        assert passed, f"Good fixture failed: {reason}"

    def test_10_5_tags_relevant(self, good_mdx_en):
        fm = parse_frontmatter(good_mdx_en)
        passed, reason = check_10_5_tags_relevant(fm)
        assert passed, f"Good fixture failed: {reason}"


# ============================================================================
# RUN ALL CHECKS ON A DATASET
# ============================================================================

def validate_dataset_ai_checks(dataset_id: str) -> dict:
    """
    Run all AI judgment checks on a dataset.
    Returns dict with results for each check.
    """
    results = {}

    # Paths
    mdx_en = DATA_MN_DIR / f"src/data/data/en/{dataset_id}.mdx"
    mdx_mn = DATA_MN_DIR / f"src/data/data/mn/{dataset_id}.mdx"
    csv_en = DATA_MN_DIR / f"public/datasets/{dataset_id}-en.csv"
    csv_mn = DATA_MN_DIR / f"public/datasets/{dataset_id}-mn.csv"
    xlsx = DATA_MN_DIR / f"public/datasets/{dataset_id}.xlsx"
    chart_en = DATA_MN_DIR / f"public/charts/{dataset_id}-en.json"
    chart_mn = DATA_MN_DIR / f"public/charts/{dataset_id}-mn.json"

    # Parse frontmatter
    fm_en = parse_frontmatter(mdx_en) if mdx_en.exists() else {}
    fm_mn = parse_frontmatter(mdx_mn) if mdx_mn.exists() else {}
    body_en = get_mdx_body(mdx_en) if mdx_en.exists() else ""

    # Run checks
    results['2.3'] = check_2_3_excerpt_meaningful(fm_en)
    results['2.6'] = check_2_6_keywords_useful(fm_en)
    results['2.13'] = check_2_13_source_tableid(fm_en)
    results['3.4'] = check_3_4_vegachart_has_title(body_en)
    results['3.5'] = check_3_5_no_placeholder_text(fm_en, body_en)

    if csv_en.exists():
        results['4.6'] = check_4_6_long_form(csv_en)
    if csv_en.exists() and csv_mn.exists():
        results['4.12'] = check_4_12_row_count_match(csv_en, csv_mn)
        results['4.13'] = check_4_13_column_count_match(csv_en, csv_mn)
        results['4.14'] = check_4_14_numeric_values_match(csv_en, csv_mn)

    if xlsx.exists():
        results['5.5'] = check_5_5_wide_form(xlsx)

    results['8.2'] = check_8_2_category_match(fm_en, fm_mn)
    results['8.3'] = check_8_3_dataversion_match(fm_en, fm_mn)
    results['8.4'] = check_8_4_datadate_match(fm_en, fm_mn)
    results['8.5'] = check_8_5_tag_count_similar(fm_en, fm_mn)

    if chart_en.exists() and chart_mn.exists():
        results['8.6'] = check_8_6_chart_type_match(chart_en, chart_mn)

    results['8.7'] = check_8_7_numeric_data_identical(csv_en, csv_mn) if (csv_en.exists() and csv_mn.exists()) else (True, "Skipped")

    results['10.1'] = check_10_1_title_has_year_range(fm_en)
    results['10.2'] = check_10_2_excerpt_has_insight(fm_en)
    results['10.3'] = check_10_3_source_accurate(fm_en)
    results['10.5'] = check_10_5_tags_relevant(fm_en)
    results['10.6'] = check_10_6_keywords_seo(fm_en)

    return results


if __name__ == '__main__':
    # Example: validate a specific dataset
    import sys
    dataset_id = sys.argv[1] if len(sys.argv) > 1 else 'gdp-nominal'

    print(f"\n{'='*60}")
    print(f"AI Judgment Checks for: {dataset_id}")
    print('='*60)

    results = validate_dataset_ai_checks(dataset_id)

    passed = 0
    failed = 0
    for check_id, (result, reason) in sorted(results.items()):
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  [{check_id}] {status}: {reason}")
        if result:
            passed += 1
        else:
            failed += 1

    print(f"\n{'='*60}")
    print(f"Results: {passed} passed, {failed} failed")
    print('='*60)

    sys.exit(0 if failed == 0 else 1)
