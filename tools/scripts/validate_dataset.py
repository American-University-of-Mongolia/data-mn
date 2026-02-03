#!/usr/bin/env python3
"""
Dataset Validation Script

Validates individual dataset files (MDX, CSV, XLSX, Chart JSON) against
the data.mn schema requirements. Designed for parallel worker validation
where a full build isn't possible.

Usage:
    python validate_dataset.py --mdx path/to/file.mdx
    python validate_dataset.py --csv path/to/file.csv
    python validate_dataset.py --xlsx path/to/file.xlsx
    python validate_dataset.py --chart path/to/chart.json
    python validate_dataset.py --all DATASET_ID  # Validates all files for a dataset
"""

import argparse
import json
import os
import sys
import re
from pathlib import Path
from typing import Optional

# Try to import optional dependencies
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False


# ============================================
# Category Configuration
# Loaded from tools/config/categories.json (single source of truth)
# ============================================
def load_categories_config():
    """Load categories from config file. Falls back to hardcoded list if file not found."""
    config_path = Path(__file__).parent.parent / 'config' / 'categories.json'

    # Default fallback categories
    fallback_en = ["Demographics", "Economy", "Labor Market", "Housing", "Mining",
                   "Finance", "Agriculture", "Education", "Health", "Trade",
                   "Energy", "Tourism", "Environment", "Transport", "Technology"]
    fallback_mn = ["Хүн ам зүй", "Эдийн засаг", "Хөдөлмөрийн зах зээл", "Орон сууц",
                   "Уул уурхай", "Санхүү", "Хөдөө аж ахуй", "Боловсрол", "Эрүүл мэнд",
                   "Худалдаа", "Эрчим хүч", "Аялал жуулчлал", "Байгаль орчин", "Тээвэр", "Технологи"]

    if not config_path.exists():
        return fallback_en, fallback_mn, {}, {}

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        categories = config.get('categories', [])
        valid_en = [cat['en'] for cat in categories]
        valid_mn = [cat['mn'] for cat in categories]

        # Load aliases for backward compatibility
        aliases = config.get('aliases', {})
        aliases_en = aliases.get('en', {})
        aliases_mn = aliases.get('mn', {})

        return valid_en, valid_mn, aliases_en, aliases_mn
    except Exception:
        return fallback_en, fallback_mn, {}, {}

# Load categories at module level
VALID_CATEGORIES_EN, VALID_CATEGORIES_MN, CATEGORY_ALIASES_EN, CATEGORY_ALIASES_MN = load_categories_config()

# Common English column headers that should be translated in MN CSVs
ENGLISH_CSV_HEADERS = ['category', 'year', 'value', 'sex', 'region', 'location',
                        'type', 'age', 'population', 'rate', 'amount', 'total']

# Expected Mongolian column headers
MONGOLIAN_CSV_HEADERS = {
    'category': 'ангилал',
    'year': 'он',
    'value': 'утга',
    'sex': 'хүйс',
    'region': 'бүс',
    'location': 'байршил',
    'type': 'төрөл',
    'age': 'нас',
    'population': 'хүн ам',
    'rate': 'түвшин',
    'amount': 'дүн',
    'total': 'нийт',
}


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class ValidationResult:
    """Holds validation results."""
    def __init__(self, file_path: str, file_type: str):
        self.file_path = file_path
        self.file_type = file_type
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []

    def add_error(self, msg: str):
        self.errors.append(msg)

    def add_warning(self, msg: str):
        self.warnings.append(msg)

    def add_info(self, msg: str):
        self.info.append(msg)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def print_report(self):
        status = "✅ VALID" if self.is_valid else "❌ INVALID"
        print(f"\n{status}: {self.file_type} - {self.file_path}")

        for msg in self.errors:
            print(f"  ❌ ERROR: {msg}")
        for msg in self.warnings:
            print(f"  ⚠️  WARNING: {msg}")
        for msg in self.info:
            print(f"  ℹ️  INFO: {msg}")

        return self.is_valid


def parse_mdx_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter from MDX content."""
    if not content.startswith('---'):
        raise ValidationError("MDX file must start with '---' frontmatter delimiter")

    # Find the closing ---
    lines = content.split('\n')
    end_index = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            end_index = i
            break

    if end_index == -1:
        raise ValidationError("Could not find closing '---' for frontmatter")

    frontmatter_text = '\n'.join(lines[1:end_index])
    body = '\n'.join(lines[end_index + 1:])

    if not HAS_YAML:
        raise ValidationError("PyYAML not installed. Run: pip install pyyaml")

    try:
        frontmatter = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as e:
        raise ValidationError(f"Invalid YAML in frontmatter: {e}")

    return frontmatter, body


def validate_mdx(file_path: str, base_dir: Optional[str] = None) -> ValidationResult:
    """Validate an MDX file against the data.mn schema."""
    result = ValidationResult(file_path, "MDX")

    # Check file exists
    if not os.path.exists(file_path):
        result.add_error(f"File does not exist: {file_path}")
        return result

    # Read file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        result.add_error(f"Could not read file: {e}")
        return result

    # Check for BOM or invisible characters at start
    if content and ord(content[0]) > 127:
        result.add_error(f"File starts with non-ASCII character (code {ord(content[0])}). May have BOM or encoding issue.")

    # Parse frontmatter
    try:
        frontmatter, body = parse_mdx_frontmatter(content)
    except ValidationError as e:
        result.add_error(str(e))
        return result

    if frontmatter is None:
        result.add_error("Frontmatter parsed as None/empty")
        return result

    # Determine language from path
    is_mongolian = '/mn/' in file_path or file_path.endswith('/mn/')
    lang = 'mn' if is_mongolian else 'en'

    # Required fields
    required_fields = ['title']
    for field in required_fields:
        if field not in frontmatter:
            result.add_error(f"Missing required field: {field}")
        elif not frontmatter[field]:
            result.add_error(f"Required field is empty: {field}")

    # Validate title
    if 'title' in frontmatter:
        title = frontmatter['title']
        if not isinstance(title, str):
            result.add_error(f"title must be a string, got {type(title).__name__}")
        elif len(title) < 5:
            result.add_warning(f"title seems too short: '{title}'")

    # Validate category
    if 'category' in frontmatter:
        cat = frontmatter['category']
        valid_cats = VALID_CATEGORIES_MN if is_mongolian else VALID_CATEGORIES_EN
        aliases = CATEGORY_ALIASES_MN if is_mongolian else CATEGORY_ALIASES_EN

        if cat not in valid_cats:
            # Check if it's an alias (old/variant name)
            if cat in aliases:
                canonical_id = aliases[cat]
                result.add_warning(
                    f"category '{cat}' is an alias. Consider using canonical name. "
                    f"(Maps to ID: {canonical_id})"
                )
            else:
                result.add_warning(f"category '{cat}' not in standard list for {lang.upper()}")

    # Validate dataFiles array
    if 'dataFiles' in frontmatter:
        data_files = frontmatter['dataFiles']
        if not isinstance(data_files, list):
            result.add_error(f"dataFiles must be a list, got {type(data_files).__name__}")
        else:
            for i, df in enumerate(data_files):
                if not isinstance(df, dict):
                    result.add_error(f"dataFiles[{i}] must be an object, got {type(df).__name__}")
                    continue

                # Check required dataFile fields
                if 'path' not in df:
                    result.add_error(f"dataFiles[{i}].path is REQUIRED but missing")
                elif not isinstance(df['path'], str):
                    result.add_error(f"dataFiles[{i}].path must be a string, got {type(df['path']).__name__}")
                elif not df['path'].startswith('/'):
                    result.add_warning(f"dataFiles[{i}].path should start with '/': {df['path']}")

                if 'format' not in df:
                    result.add_error(f"dataFiles[{i}].format is REQUIRED but missing")
                elif df['format'] not in ['csv', 'xlsx', 'json', 'pdf']:
                    result.add_warning(f"dataFiles[{i}].format unusual: {df['format']}")

                # Check if referenced file exists
                if base_dir and 'path' in df and isinstance(df['path'], str):
                    ref_path = os.path.join(base_dir, 'public', df['path'].lstrip('/'))
                    if not os.path.exists(ref_path):
                        result.add_warning(f"Referenced file does not exist: {df['path']}")
    else:
        result.add_warning("No dataFiles defined - downloads won't be available")

    # Validate source
    if 'source' in frontmatter:
        source = frontmatter['source']
        if not isinstance(source, dict):
            result.add_error(f"source must be an object, got {type(source).__name__}")
        else:
            if 'name' not in source:
                result.add_warning("source.name is recommended")
            if 'url' not in source:
                result.add_warning("source.url is recommended")
            elif source['url'] and not source['url'].startswith('http'):
                result.add_error(f"source.url must be a valid URL: {source['url']}")

    # Validate tags
    if 'tags' in frontmatter:
        tags = frontmatter['tags']
        if not isinstance(tags, list):
            result.add_error(f"tags must be a list, got {type(tags).__name__}")
        else:
            for tag in tags:
                if not isinstance(tag, str):
                    result.add_error(f"Each tag must be a string, got {type(tag).__name__}")

    # Check body has VegaChart
    if 'VegaChart' not in body:
        result.add_warning("Body does not contain VegaChart component")

    # Check import statement
    if "import VegaChart from '~/components/ui/VegaChart.astro'" not in body:
        result.add_warning("Missing VegaChart import statement")

    # ============================================
    # Check for forbidden sections in MDX body
    # Data pages must be minimal - the chart IS the content
    # Includes both English and Mongolian patterns
    # ============================================
    FORBIDDEN_HEADINGS = [
        # English patterns
        (r'^##\s*Key\s*Findings', 'Key Findings'),
        (r'^##\s*Overview', 'Overview'),
        (r'^##\s*Analysis', 'Analysis'),
        (r'^##\s*Data\s*Breakdown', 'Data Breakdown'),
        (r'^##\s*Trend', 'Trend'),
        (r'^##\s*Comparison', 'Comparison'),
        (r'^##\s*About\s*the\s*Data', 'About the Data'),
        (r'^##\s*Download\s*Data', 'Download Data'),
        (r'^##\s*Source', 'Source'),
        (r'^##\s*Methodology', 'Methodology'),
        # Mongolian patterns (translations of above)
        (r'^##\s*Гол\s*үзүүлэлтүүд', 'Гол үзүүлэлтүүд (Key Findings)'),
        (r'^##\s*Тойм', 'Тойм (Overview)'),
        (r'^##\s*Шинжилгээ', 'Шинжилгээ (Analysis)'),
        (r'^##\s*Өгөгдлийн\s*задаргаа', 'Өгөгдлийн задаргаа (Data Breakdown)'),
        (r'^##\s*Хандлага', 'Хандлага (Trend)'),
        (r'^##\s*Харьцуулалт', 'Харьцуулалт (Comparison)'),
        (r'^##\s*Өгөгдлийн\s*тухай', 'Өгөгдлийн тухай (About the Data)'),
        (r'^##\s*Өгөгдөл\s*татах', 'Өгөгдөл татах (Download Data)'),
        (r'^##\s*Эх\s*сурвалж', 'Эх сурвалж (Source)'),
        (r'^##\s*Арга\s*зүй', 'Арга зүй (Methodology)'),
    ]

    for pattern, name in FORBIDDEN_HEADINGS:
        if re.search(pattern, body, re.IGNORECASE | re.MULTILINE):
            result.add_error(
                f"MDX body contains forbidden section: '{name}'. "
                f"Data pages must be minimal - the chart IS the content. "
                f"Remove all prose sections."
            )

    # Check for content after VegaChart (should be empty or whitespace only)
    vegachart_match = re.search(r'<VegaChart[^>]*/>', body)
    if vegachart_match:
        content_after_chart = body[vegachart_match.end():].strip()
        if content_after_chart:
            # Allow closing tags but nothing else
            if not re.match(r'^(\s|<\/\w+>)*$', content_after_chart):
                result.add_error(
                    f"MDX has content after VegaChart component. "
                    f"Data pages must end with the chart - no Key Findings, "
                    f"Analysis, or other sections allowed."
                )

    result.add_info(f"Frontmatter has {len(frontmatter)} fields")

    return result


def validate_csv(file_path: str) -> ValidationResult:
    """Validate a CSV data file."""
    result = ValidationResult(file_path, "CSV")

    if not os.path.exists(file_path):
        result.add_error(f"File does not exist: {file_path}")
        return result

    # Check file size
    size = os.path.getsize(file_path)
    if size == 0:
        result.add_error("CSV file is empty (0 bytes)")
        return result

    result.add_info(f"File size: {size:,} bytes")

    if not HAS_PANDAS:
        result.add_warning("pandas not installed - skipping content validation")
        return result

    # Try to read CSV
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        result.add_error(f"Could not parse CSV: {e}")
        return result

    # Check row count
    if len(df) == 0:
        result.add_error("CSV has no data rows")
        return result

    result.add_info(f"Rows: {len(df)}, Columns: {len(df.columns)}")

    # Check for common issues
    if df.columns.duplicated().any():
        result.add_error(f"Duplicate column names found")

    # Check for completely empty columns
    empty_cols = [col for col in df.columns if df[col].isna().all()]
    if empty_cols:
        result.add_warning(f"Empty columns: {empty_cols}")

    # Check column naming conventions
    for col in df.columns:
        if col != col.lower():
            result.add_warning(f"Column '{col}' should be lowercase")
        if ' ' in col:
            result.add_warning(f"Column '{col}' contains spaces (use underscores)")

    # Check for expected columns in time series data
    if 'year' in [c.lower() for c in df.columns]:
        year_col = [c for c in df.columns if c.lower() == 'year'][0]
        years = df[year_col].dropna()
        if len(years) > 0:
            result.add_info(f"Year range: {int(years.min())} - {int(years.max())}")

    # ============================================
    # NEW: Check for leading/trailing whitespace in string values
    # This catches the bug where category values like "   Female"
    # don't match chart color domains ["Male", "Female"]
    # ============================================
    string_cols = df.select_dtypes(include=['object']).columns
    for col in string_cols:
        # Check for leading whitespace
        leading_ws = df[col].astype(str).str.match(r'^\s+')
        if leading_ws.any():
            bad_values = df[col][leading_ws].unique()[:3]  # Show first 3
            result.add_error(
                f"Column '{col}' has values with LEADING WHITESPACE: {list(bad_values)}. "
                f"This will break chart color matching!"
            )

        # Check for trailing whitespace
        trailing_ws = df[col].astype(str).str.match(r'.*\s+$')
        if trailing_ws.any():
            bad_values = df[col][trailing_ws].unique()[:3]
            result.add_warning(
                f"Column '{col}' has values with trailing whitespace: {list(bad_values)}"
            )

    # Check for completely whitespace-only values
    for col in string_cols:
        ws_only = df[col].astype(str).str.match(r'^\s*$')
        non_null_ws = ws_only & df[col].notna()
        if non_null_ws.any():
            result.add_warning(
                f"Column '{col}' has whitespace-only values (not null, just spaces)"
            )

    # ============================================
    # NEW: Check CSV headers are in correct language
    # (Check #13 from validation checklist)
    # ============================================
    is_mongolian_csv = '-mn.csv' in file_path or '/mn/' in file_path
    if is_mongolian_csv:
        # MN CSV should have Mongolian column headers
        english_headers_found = []
        for col in df.columns:
            col_lower = col.lower().strip()
            if col_lower in ENGLISH_CSV_HEADERS:
                expected_mn = MONGOLIAN_CSV_HEADERS.get(col_lower, '[unknown]')
                english_headers_found.append((col, expected_mn))

        if english_headers_found:
            header_list = ", ".join([f"'{h[0]}'→'{h[1]}'" for h in english_headers_found])
            result.add_error(
                f"MN CSV has English column headers! Found: {header_list}. "
                f"Mongolian CSVs must use translated headers for consistency with MN charts."
            )

    return result


def validate_xlsx(file_path: str) -> ValidationResult:
    """Validate an Excel file."""
    result = ValidationResult(file_path, "XLSX")

    if not os.path.exists(file_path):
        result.add_error(f"File does not exist: {file_path}")
        return result

    # Check file size
    size = os.path.getsize(file_path)
    if size == 0:
        result.add_error("XLSX file is empty (0 bytes)")
        return result

    result.add_info(f"File size: {size:,} bytes")

    if not HAS_OPENPYXL:
        result.add_warning("openpyxl not installed - skipping content validation")
        return result

    # Try to open workbook
    try:
        from openpyxl import load_workbook
        wb = load_workbook(file_path, read_only=True)
    except Exception as e:
        result.add_error(f"Could not open Excel file: {e}")
        return result

    # Check sheets
    sheet_names = wb.sheetnames
    if len(sheet_names) == 0:
        result.add_error("XLSX has no sheets")
        return result

    result.add_info(f"Sheets: {sheet_names}")

    # Check first sheet has data
    ws = wb.active
    if ws.max_row <= 1:
        result.add_warning("First sheet appears to have no data rows")
    else:
        result.add_info(f"Active sheet: {ws.max_row} rows, {ws.max_column} columns")

    wb.close()
    return result


def validate_chart(file_path: str, data_path: Optional[str] = None) -> ValidationResult:
    """Validate a Vega-Lite chart specification."""
    result = ValidationResult(file_path, "Chart JSON")

    if not os.path.exists(file_path):
        result.add_error(f"File does not exist: {file_path}")
        return result

    # Read and parse JSON
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            spec = json.load(f)
    except json.JSONDecodeError as e:
        result.add_error(f"Invalid JSON: {e}")
        return result
    except Exception as e:
        result.add_error(f"Could not read file: {e}")
        return result

    # Check required Vega-Lite fields
    if '$schema' not in spec:
        result.add_warning("Missing $schema field")

    # Check for hardcoded width/height (should be responsive)
    if 'width' in spec and isinstance(spec['width'], (int, float)):
        result.add_warning(f"Hardcoded width={spec['width']} - should use 'container' for responsive")
    if 'height' in spec and isinstance(spec['height'], (int, float)):
        result.add_warning(f"Hardcoded height={spec['height']} - consider responsive design")

    # Check data source
    if 'data' in spec:
        data = spec['data']
        if isinstance(data, dict) and 'url' in data:
            result.add_info(f"Data source: {data['url']}")

    # Check encoding
    encoding = spec.get('encoding', {})
    if not encoding:
        # Check for layer structure
        if 'layer' in spec:
            result.add_info("Layered chart with multiple encodings")
        else:
            result.add_warning("No encoding found - chart may not render")

    # Check for year field type (should be quantitative, not ordinal)
    def check_encoding_types(enc: dict, path: str = ""):
        for field_name, field_def in enc.items():
            if isinstance(field_def, dict):
                if field_def.get('field', '').lower() == 'year':
                    field_type = field_def.get('type', '')
                    if field_type == 'ordinal':
                        result.add_warning(f"{path}{field_name}: year field should be 'quantitative' not 'ordinal'")

    if encoding:
        check_encoding_types(encoding)

    result.add_info(f"Spec size: {len(json.dumps(spec)):,} chars")

    # ============================================
    # NEW: Check chart naming convention (must have language suffix)
    # ============================================
    filename = os.path.basename(file_path)
    if not (filename.endswith('-en.json') or filename.endswith('-mn.json')):
        result.add_warning(
            f"Chart file '{filename}' should have language suffix (-en.json or -mn.json). "
            f"Bilingual charts are required!"
        )

    # ============================================
    # NEW: Check data URL matches language suffix
    # ============================================
    if 'data' in spec and isinstance(spec['data'], dict):
        data_url = spec['data'].get('url', '')
        if data_url:
            if filename.endswith('-en.json'):
                if '-en.csv' not in data_url and '-en.' not in data_url:
                    result.add_warning(
                        f"EN chart should use EN data file. "
                        f"Chart: {filename}, Data URL: {data_url}"
                    )
            elif filename.endswith('-mn.json'):
                if '-mn.csv' not in data_url and '-mn.' not in data_url:
                    result.add_warning(
                        f"MN chart should use MN data file. "
                        f"Chart: {filename}, Data URL: {data_url}"
                    )

    return result


def validate_chart_csv_consistency(chart_path: str, csv_path: str) -> ValidationResult:
    """
    Cross-validate chart color domain against CSV categorical values.

    This catches bugs where:
    - Chart expects ["Male", "Female"] but CSV has ["   Male", "   Female"] (whitespace)
    - Chart expects ["Exports", "Imports"] but MN CSV has ["Экспорт", "Импорт"] (language mismatch)
    - Chart expects ["Urban", "Rural"] but CSV has different spelling
    """
    result = ValidationResult(f"{chart_path} + {os.path.basename(csv_path)}", "Chart-CSV Cross-Validation")

    if not os.path.exists(chart_path) or not os.path.exists(csv_path):
        result.add_info("Skipping cross-validation (files don't exist)")
        return result

    if not HAS_PANDAS:
        result.add_warning("pandas not installed - skipping cross-validation")
        return result

    # Load chart spec
    try:
        with open(chart_path, 'r') as f:
            spec = json.load(f)
    except Exception as e:
        result.add_error(f"Could not load chart: {e}")
        return result

    # Load CSV
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        result.add_error(f"Could not load CSV: {e}")
        return result

    # Extract color encoding domain from chart
    color_domain = None
    color_field = None

    # Check top-level encoding
    encoding = spec.get('encoding', {})
    color_enc = encoding.get('color', {})
    if isinstance(color_enc, dict):
        scale = color_enc.get('scale', {})
        if 'domain' in scale:
            color_domain = scale['domain']
            color_field = color_enc.get('field')

    # Also check layers
    for layer in spec.get('layer', []):
        layer_enc = layer.get('encoding', {})
        layer_color = layer_enc.get('color', {})
        if isinstance(layer_color, dict):
            layer_scale = layer_color.get('scale', {})
            if 'domain' in layer_scale and color_domain is None:
                color_domain = layer_scale['domain']
                color_field = layer_color.get('field')

    if color_domain and color_field:
        # Check if CSV has this field
        if color_field in df.columns:
            csv_values = df[color_field].dropna().unique().tolist()
            csv_values_str = [str(v) for v in csv_values]
            csv_values_clean = [str(v).strip() for v in csv_values]

            # Count how many domain values are missing from CSV
            missing_count = 0
            for domain_val in color_domain:
                if domain_val not in csv_values_str:
                    missing_count += 1
                    if domain_val in csv_values_clean:
                        result.add_error(
                            f"Color domain value '{domain_val}' not in CSV (but found after stripping whitespace). "
                            f"CSV has whitespace issues in column '{color_field}'!"
                        )

            # If ALL domain values are missing, this is a critical error (likely language mismatch)
            if missing_count == len(color_domain):
                result.add_error(
                    f"CRITICAL: ALL color domain values are missing from CSV! "
                    f"Chart domain: {color_domain}, CSV values: {csv_values_str[:5]}. "
                    f"This will cause the chart to show NO DATA. "
                    f"Likely a language mismatch (EN domain in MN chart or vice versa)."
                )
            elif missing_count > 0:
                # Some values missing - report which ones
                for domain_val in color_domain:
                    if domain_val not in csv_values_str and domain_val not in csv_values_clean:
                        result.add_warning(
                            f"Color domain value '{domain_val}' not found in CSV column '{color_field}'. "
                            f"CSV values: {csv_values_str[:5]}"
                        )

            # Check for CSV values not in domain (may not render with expected colors)
            for csv_val in csv_values_str:
                if csv_val not in color_domain:
                    result.add_warning(
                        f"CSV value '{csv_val}' not in chart color domain. May use default color."
                    )
        else:
            result.add_warning(f"Color field '{color_field}' not found in CSV columns: {list(df.columns)}")
    else:
        result.add_info("No color domain defined in chart (categorical comparison skipped)")

    return result


def validate_all(dataset_id: str, base_dir: str) -> list[ValidationResult]:
    """Validate all files for a dataset."""
    results = []

    # ============================================
    # NEW: Check #5 - Dataset definition file exists
    # ============================================
    definition_result = ValidationResult(f"Definition check for {dataset_id}", "Definition File")

    # Try to find definition file for common sources
    sources_dir = os.path.join(base_dir, '..', 'tools', 'sources')
    possible_sources = ['nso-1212', 'mrpam', 'mongolbank']
    definition_found = False

    for source in possible_sources:
        definition_path = os.path.join(sources_dir, source, 'datasets', f'{dataset_id}.md')
        if os.path.exists(definition_path):
            definition_found = True
            definition_result.add_info(f"Definition file found: {definition_path}")
            break

    if not definition_found:
        # Also check if this is a split dataset (has parent)
        # Parent datasets may have the definition
        parent_id = None
        if '-by-' in dataset_id or '-total' in dataset_id or '-pyramid' in dataset_id:
            # Try to find the parent dataset definition
            # Pattern: "population-by-age" -> might be from "nso-population-by-age-sex"
            definition_result.add_warning(
                f"No dataset definition file found at tools/sources/*/datasets/{dataset_id}.md. "
                f"Definition files are required for reproducible data pipelines. "
                f"If this is a split dataset, the parent should have a definition."
            )
        else:
            definition_result.add_error(
                f"Missing dataset definition file! Expected at: tools/sources/<source>/datasets/{dataset_id}.md. "
                f"Definition files are REQUIRED for data pipeline reproducibility."
            )

    results.append(definition_result)

    # ============================================
    # NEW: Check #6 - Raw data backup exists
    # ============================================
    versions_result = ValidationResult(f"Versions check for {dataset_id}", "Version Backup")

    versions_dir = os.path.join(base_dir, '..', 'tools', 'versions', dataset_id)
    if os.path.exists(versions_dir) and os.path.isdir(versions_dir):
        version_files = os.listdir(versions_dir)
        if version_files:
            versions_result.add_info(f"Version backup found: {len(version_files)} files in {versions_dir}")
        else:
            versions_result.add_warning(f"Version directory exists but is empty: {versions_dir}")
    else:
        # For split datasets, check parent version directory
        if '-by-' in dataset_id or '-total' in dataset_id:
            versions_result.add_warning(
                f"No version backup directory at tools/versions/{dataset_id}/. "
                f"Raw data should be versioned for reproducibility. "
                f"Split datasets may use parent's version directory."
            )
        else:
            versions_result.add_error(
                f"Missing version backup directory! Expected at: tools/versions/{dataset_id}/. "
                f"Raw data MUST be versioned for reproducibility and audit trails."
            )

    results.append(versions_result)

    # Define expected file paths
    files_to_check = {
        'mdx_en': f"{base_dir}/src/data/data/en/{dataset_id}.mdx",
        'mdx_mn': f"{base_dir}/src/data/data/mn/{dataset_id}.mdx",
        'csv_en': f"{base_dir}/public/datasets/{dataset_id}-en.csv",
        'csv_mn': f"{base_dir}/public/datasets/{dataset_id}-mn.csv",
        'xlsx': f"{base_dir}/public/datasets/{dataset_id}.xlsx",
        'chart_en': f"{base_dir}/public/charts/{dataset_id}-en.json",
        'chart_mn': f"{base_dir}/public/charts/{dataset_id}-mn.json",
    }

    # Also check non-suffixed versions (some datasets use this)
    alt_files = {
        'csv': f"{base_dir}/public/datasets/{dataset_id}.csv",
        'chart': f"{base_dir}/public/charts/{dataset_id}.json",
    }

    # Validate MDX files
    for key in ['mdx_en', 'mdx_mn']:
        if os.path.exists(files_to_check[key]):
            results.append(validate_mdx(files_to_check[key], base_dir))

    # Validate CSV files (check both patterns)
    csv_found = False
    csv_files_found = []
    for key in ['csv_en', 'csv_mn']:
        if os.path.exists(files_to_check[key]):
            results.append(validate_csv(files_to_check[key]))
            csv_files_found.append((key, files_to_check[key]))
            csv_found = True
    if not csv_found and os.path.exists(alt_files['csv']):
        results.append(validate_csv(alt_files['csv']))
        csv_files_found.append(('csv', alt_files['csv']))

    # Validate XLSX
    if os.path.exists(files_to_check['xlsx']):
        results.append(validate_xlsx(files_to_check['xlsx']))

    # Validate charts (check both patterns)
    chart_found = False
    chart_files_found = []
    for key in ['chart_en', 'chart_mn']:
        if os.path.exists(files_to_check[key]):
            results.append(validate_chart(files_to_check[key]))
            chart_files_found.append((key, files_to_check[key]))
            chart_found = True
    if not chart_found and os.path.exists(alt_files['chart']):
        results.append(validate_chart(alt_files['chart']))
        chart_files_found.append(('chart', alt_files['chart']))

    # ============================================
    # NEW: Cross-validate chart-CSV consistency
    # ============================================
    # Match chart_en with csv_en, chart_mn with csv_mn
    for chart_key, chart_path in chart_files_found:
        matching_csv = None
        if chart_key == 'chart_en' and os.path.exists(files_to_check['csv_en']):
            matching_csv = files_to_check['csv_en']
        elif chart_key == 'chart_mn' and os.path.exists(files_to_check['csv_mn']):
            matching_csv = files_to_check['csv_mn']
        elif chart_key == 'chart' and len(csv_files_found) > 0:
            matching_csv = csv_files_found[0][1]

        if matching_csv:
            results.append(validate_chart_csv_consistency(chart_path, matching_csv))

    return results


def main():
    parser = argparse.ArgumentParser(description='Validate dataset files')
    parser.add_argument('--mdx', help='Path to MDX file to validate')
    parser.add_argument('--csv', help='Path to CSV file to validate')
    parser.add_argument('--xlsx', help='Path to XLSX file to validate')
    parser.add_argument('--chart', help='Path to chart JSON file to validate')
    parser.add_argument('--all', metavar='DATASET_ID', help='Validate all files for a dataset')
    parser.add_argument('--base-dir', default='data/data.mn', help='Base directory for data.mn project')

    args = parser.parse_args()

    results = []

    if args.mdx:
        results.append(validate_mdx(args.mdx, args.base_dir))

    if args.csv:
        results.append(validate_csv(args.csv))

    if args.xlsx:
        results.append(validate_xlsx(args.xlsx))

    if args.chart:
        results.append(validate_chart(args.chart))

    if args.all:
        results.extend(validate_all(args.all, args.base_dir))

    if not results:
        print("No files specified. Use --mdx, --csv, --xlsx, --chart, or --all DATASET_ID")
        sys.exit(1)

    # Print results
    all_valid = True
    for result in results:
        if not result.print_report():
            all_valid = False

    # Summary
    print(f"\n{'='*50}")
    print(f"Validated {len(results)} file(s)")
    valid_count = sum(1 for r in results if r.is_valid)
    print(f"✅ Valid: {valid_count}")
    print(f"❌ Invalid: {len(results) - valid_count}")

    sys.exit(0 if all_valid else 1)


if __name__ == '__main__':
    main()
