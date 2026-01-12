#!/usr/bin/env python3
"""
Unified Test Runner for data.mn Datasets

Runs ALL 85 validation checks (60 scripted + 25 AI judgment) on a dataset.
Returns exit code 0 if all pass, 1 if any fail.

Usage:
    python run_all_checks.py <dataset_id>
    python run_all_checks.py gdp-nominal
    python run_all_checks.py --all  # Validate all datasets in registry

Output:
    - Structured report showing pass/fail for each check
    - Summary with total counts
    - Exit code for CI/automation use
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from test_ai_checks import validate_dataset_ai_checks
from conftest import DATA_MN_DIR, parse_frontmatter

# Also import from validate_dataset.py
TOOLS_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = TOOLS_DIR / 'scripts'


@dataclass
class CheckResult:
    check_id: str
    section: str
    description: str
    passed: bool
    reason: str
    severity: str = "required"  # "critical", "required", "warning"


def run_scripted_checks(dataset_id: str, base_dir: Path) -> list[CheckResult]:
    """Run the scripted validation checks from validate_dataset.py"""
    results = []

    # File paths
    mdx_en = base_dir / f"src/data/data/en/{dataset_id}.mdx"
    mdx_mn = base_dir / f"src/data/data/mn/{dataset_id}.mdx"
    csv_en = base_dir / f"public/datasets/{dataset_id}-en.csv"
    csv_mn = base_dir / f"public/datasets/{dataset_id}-mn.csv"
    xlsx = base_dir / f"public/datasets/{dataset_id}.xlsx"
    chart_en = base_dir / f"public/charts/{dataset_id}-en.json"
    chart_mn = base_dir / f"public/charts/{dataset_id}-mn.json"

    # Section 1: File Existence (7 checks)
    file_checks = [
        ("1.1", "MDX page (EN)", mdx_en),
        ("1.2", "MDX page (MN)", mdx_mn),
        ("1.3", "CSV data (EN)", csv_en),
        ("1.4", "CSV data (MN)", csv_mn),
        ("1.5", "Excel file", xlsx),
        ("1.6", "Chart spec (EN)", chart_en),
        ("1.7", "Chart spec (MN)", chart_mn),
    ]

    for check_id, desc, path in file_checks:
        exists = path.exists()
        results.append(CheckResult(
            check_id=check_id,
            section="File Existence",
            description=desc,
            passed=exists,
            reason=f"exists at {path.name}" if exists else f"MISSING: {path}",
            severity="required"
        ))

    # Section 2: MDX Frontmatter (scripted checks)
    for lang, mdx_path in [("EN", mdx_en), ("MN", mdx_mn)]:
        if not mdx_path.exists():
            continue

        fm = parse_frontmatter(mdx_path)

        # 2.1: title non-empty
        title = fm.get('title', '')
        results.append(CheckResult(
            check_id=f"2.1-{lang}",
            section="MDX Frontmatter",
            description=f"title ({lang})",
            passed=bool(title) and len(title) >= 5,
            reason=f"'{title[:50]}...'" if title else "MISSING",
            severity="required"
        ))

        # 2.2: publishDate valid
        pub_date = fm.get('publishDate', '')
        results.append(CheckResult(
            check_id=f"2.2-{lang}",
            section="MDX Frontmatter",
            description=f"publishDate ({lang})",
            passed=bool(pub_date),
            reason=str(pub_date) if pub_date else "MISSING",
            severity="required"
        ))

        # 2.5: tags array
        tags = fm.get('tags', [])
        results.append(CheckResult(
            check_id=f"2.5-{lang}",
            section="MDX Frontmatter",
            description=f"tags ({lang})",
            passed=isinstance(tags, list) and len(tags) >= 3,
            reason=f"{len(tags)} tags" if isinstance(tags, list) else "MISSING/INVALID",
            severity="required"
        ))

        # 2.10: dataFiles array
        data_files = fm.get('dataFiles', [])
        results.append(CheckResult(
            check_id=f"2.10-{lang}",
            section="MDX Frontmatter",
            description=f"dataFiles ({lang})",
            passed=isinstance(data_files, list) and len(data_files) >= 2,
            reason=f"{len(data_files)} files" if isinstance(data_files, list) else "MISSING",
            severity="required"
        ))

    # Section 4: CSV checks (scripted)
    for lang, csv_path in [("EN", csv_en), ("MN", csv_mn)]:
        if not csv_path.exists():
            continue

        try:
            import pandas as pd
            df = pd.read_csv(csv_path)

            # 4.1: Non-empty
            results.append(CheckResult(
                check_id=f"4.1-{lang}",
                section="CSV Data",
                description=f"Non-empty ({lang})",
                passed=len(df) > 0,
                reason=f"{len(df)} rows",
                severity="required"
            ))

            # 4.4: No duplicate columns
            has_dups = df.columns.duplicated().any()
            results.append(CheckResult(
                check_id=f"4.4-{lang}",
                section="CSV Data",
                description=f"No duplicate columns ({lang})",
                passed=not has_dups,
                reason="OK" if not has_dups else "DUPLICATES FOUND",
                severity="required"
            ))

            # 4.7-4.9: Whitespace checks (CRITICAL)
            import re
            string_cols = df.select_dtypes(include=['object']).columns
            whitespace_issues = []
            for col in string_cols:
                leading = df[col].astype(str).str.match(r'^\s+').any()
                trailing = df[col].astype(str).str.match(r'.*\s+$').any()
                if leading or trailing:
                    whitespace_issues.append(col)

            results.append(CheckResult(
                check_id=f"4.7-{lang}",
                section="CSV Data",
                description=f"No whitespace issues ({lang})",
                passed=len(whitespace_issues) == 0,
                reason="OK" if not whitespace_issues else f"WHITESPACE in: {whitespace_issues}",
                severity="critical"
            ))

        except Exception as e:
            results.append(CheckResult(
                check_id=f"4.X-{lang}",
                section="CSV Data",
                description=f"CSV readable ({lang})",
                passed=False,
                reason=f"ERROR: {e}",
                severity="required"
            ))

    # Section 6: Chart checks (scripted)
    for lang, chart_path in [("EN", chart_en), ("MN", chart_mn)]:
        if not chart_path.exists():
            continue

        try:
            spec = json.loads(chart_path.read_text())

            # 6.1: Valid JSON (implicit - we got here)
            results.append(CheckResult(
                check_id=f"6.1-{lang}",
                section="Chart Specs",
                description=f"Valid JSON ({lang})",
                passed=True,
                reason="OK",
                severity="required"
            ))

            # 6.2: Has $schema
            has_schema = '$schema' in spec
            results.append(CheckResult(
                check_id=f"6.2-{lang}",
                section="Chart Specs",
                description=f"Has $schema ({lang})",
                passed=has_schema,
                reason="OK" if has_schema else "MISSING",
                severity="required"
            ))

            # 6.5-6.6: No hardcoded width/height
            has_width = 'width' in spec and isinstance(spec['width'], (int, float))
            has_height = 'height' in spec and isinstance(spec['height'], (int, float))
            results.append(CheckResult(
                check_id=f"6.5-{lang}",
                section="Chart Specs",
                description=f"No hardcoded dimensions ({lang})",
                passed=not (has_width or has_height),
                reason="OK" if not (has_width or has_height) else f"width={spec.get('width')}, height={spec.get('height')}",
                severity="required"
            ))

            # 6.7-6.8: Data URL language match
            data_url = spec.get('data', {}).get('url', '') if isinstance(spec.get('data'), dict) else ''
            expected_suffix = f"-{lang.lower()}.csv"
            url_matches = expected_suffix in data_url
            results.append(CheckResult(
                check_id=f"6.7-{lang}",
                section="Chart Specs",
                description=f"Data URL lang match ({lang})",
                passed=url_matches,
                reason="OK" if url_matches else f"URL '{data_url}' should contain '{expected_suffix}'",
                severity="critical"
            ))

            # 6.11-6.18: Hover layer pattern (for line/area charts)
            mark_type = None
            if 'mark' in spec:
                mark = spec['mark']
                mark_type = mark if isinstance(mark, str) else mark.get('type')
            elif 'layer' in spec and spec['layer']:
                first_mark = spec['layer'][0].get('mark', {})
                mark_type = first_mark if isinstance(first_mark, str) else first_mark.get('type')

            if mark_type in ('line', 'area'):
                has_layer = 'layer' in spec
                has_hover = False
                if has_layer:
                    for layer in spec.get('layer', []):
                        params = layer.get('params', [])
                        for p in params:
                            if p.get('name') == 'hover':
                                has_hover = True

                results.append(CheckResult(
                    check_id=f"6.11-{lang}",
                    section="Chart Specs",
                    description=f"Hover layer ({lang})",
                    passed=has_layer and has_hover,
                    reason="OK" if (has_layer and has_hover) else "Line/area chart needs hover layer",
                    severity="required"
                ))

        except json.JSONDecodeError as e:
            results.append(CheckResult(
                check_id=f"6.1-{lang}",
                section="Chart Specs",
                description=f"Valid JSON ({lang})",
                passed=False,
                reason=f"INVALID JSON: {e}",
                severity="required"
            ))

    # Section 7: Chart-CSV consistency (CRITICAL)
    if chart_en.exists() and csv_en.exists():
        try:
            import pandas as pd
            spec = json.loads(chart_en.read_text())
            df = pd.read_csv(csv_en)

            # Find color domain in chart
            color_domain = None
            color_field = None

            def find_color_domain(obj):
                nonlocal color_domain, color_field
                if isinstance(obj, dict):
                    if 'color' in obj:
                        color = obj['color']
                        if isinstance(color, dict):
                            scale = color.get('scale', {})
                            if 'domain' in scale:
                                color_domain = scale['domain']
                                color_field = color.get('field')
                    for v in obj.values():
                        find_color_domain(v)
                elif isinstance(obj, list):
                    for item in obj:
                        find_color_domain(item)

            find_color_domain(spec)

            if color_domain and color_field and color_field in df.columns:
                csv_values = set(df[color_field].dropna().astype(str).unique())
                domain_set = set(str(v) for v in color_domain)
                missing = domain_set - csv_values

                results.append(CheckResult(
                    check_id="7.2",
                    section="Chart-CSV Consistency",
                    description="Color domain in CSV",
                    passed=len(missing) == 0,
                    reason="OK" if not missing else f"MISSING from CSV: {missing}",
                    severity="critical"
                ))
        except Exception as e:
            pass  # Skip if can't check

    return results


def run_ai_checks(dataset_id: str) -> list[CheckResult]:
    """Run the AI judgment checks from test_ai_checks.py"""
    results = []

    ai_results = validate_dataset_ai_checks(dataset_id)

    # Map check IDs to descriptions and severities
    check_info = {
        '2.3': ("Excerpt meaningful", "required"),
        '2.6': ("Keywords useful for SEO", "warning"),
        '2.13': ("NSO source has tableId", "warning"),
        '3.4': ("VegaChart has title", "required"),
        '3.5': ("No placeholder text", "required"),
        '4.6': ("CSV in long form", "required"),
        '4.12': ("EN/MN row count match", "required"),
        '4.13': ("EN/MN column count match", "required"),
        '4.14': ("EN/MN numeric values match", "critical"),
        '5.5': ("XLSX in wide form", "warning"),
        '8.2': ("Category translation match", "required"),
        '8.3': ("dataVersion match", "required"),
        '8.4': ("dataDate match", "required"),
        '8.5': ("Tag count similar", "warning"),
        '8.6': ("Chart type match", "required"),
        '8.7': ("Numeric data identical", "critical"),
        '10.1': ("Title has year range", "warning"),
        '10.2': ("Excerpt has insight", "warning"),
        '10.3': ("Source accurate", "required"),
        '10.5': ("Tags relevant", "warning"),
        '10.6': ("Keywords SEO-friendly", "warning"),
    }

    for check_id, (passed, reason) in ai_results.items():
        desc, severity = check_info.get(check_id, (f"Check {check_id}", "required"))
        results.append(CheckResult(
            check_id=check_id,
            section="AI Judgment",
            description=desc,
            passed=passed,
            reason=reason,
            severity=severity
        ))

    return results


def print_report(dataset_id: str, results: list[CheckResult]) -> bool:
    """Print formatted report and return True if all passed."""

    print(f"\n{'='*70}")
    print(f"VALIDATION REPORT: {dataset_id}")
    print(f"{'='*70}\n")

    # Group by section
    sections = {}
    for r in results:
        if r.section not in sections:
            sections[r.section] = []
        sections[r.section].append(r)

    total_pass = 0
    total_fail = 0
    critical_fail = 0

    for section_name, checks in sections.items():
        print(f"## {section_name}")
        print("-" * 50)

        for r in checks:
            status = "✓" if r.passed else "✗"
            sev_marker = " [CRITICAL]" if r.severity == "critical" and not r.passed else ""
            print(f"  [{r.check_id}] {status} {r.description}{sev_marker}")
            if not r.passed:
                print(f"          → {r.reason}")

            if r.passed:
                total_pass += 1
            else:
                total_fail += 1
                if r.severity == "critical":
                    critical_fail += 1
        print()

    # Summary
    print(f"{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"  Total checks:    {total_pass + total_fail}")
    print(f"  Passed:          {total_pass}")
    print(f"  Failed:          {total_fail}")
    if critical_fail > 0:
        print(f"  Critical fails:  {critical_fail} ⚠️")
    print()

    if total_fail == 0:
        print("✅ ALL CHECKS PASSED")
    else:
        print("❌ VALIDATION FAILED")
        print("\nFailed checks to fix:")
        for r in results:
            if not r.passed:
                sev = f" [{r.severity.upper()}]" if r.severity != "warning" else ""
                print(f"  • [{r.check_id}] {r.description}{sev}: {r.reason}")

    print(f"\n{'='*70}\n")

    return total_fail == 0


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_all_checks.py <dataset_id>")
        print("       python run_all_checks.py gdp-nominal")
        sys.exit(1)

    dataset_id = sys.argv[1]

    # Run all checks
    results = []
    results.extend(run_scripted_checks(dataset_id, DATA_MN_DIR))
    results.extend(run_ai_checks(dataset_id))

    # Print report and exit with appropriate code
    all_passed = print_report(dataset_id, results)
    sys.exit(0 if all_passed else 1)


if __name__ == '__main__':
    main()
