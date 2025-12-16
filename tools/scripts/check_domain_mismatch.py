#!/usr/bin/env python3
"""
Check all charts for color domain mismatches with their CSV data.

This script identifies cases where a chart's color scale domain
contains values that don't exist in the corresponding CSV file.
"""

import json
import csv
from pathlib import Path
from typing import Optional


def get_csv_unique_values(csv_path: Path, field: str) -> set[str]:
    """Get unique values for a field from a CSV file."""
    if not csv_path.exists():
        return set()

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        values = set()
        for row in reader:
            if field in row:
                values.add(row[field].strip())
    return values


def extract_color_encoding(chart: dict) -> Optional[dict]:
    """Extract color encoding from chart, handling layers."""
    # Direct encoding
    if 'encoding' in chart and 'color' in chart.get('encoding', {}):
        return chart['encoding']['color']

    # Check layers
    for layer in chart.get('layer', []):
        if 'encoding' in layer and 'color' in layer.get('encoding', {}):
            return layer['encoding']['color']

    return None


def check_chart(chart_path: Path, datasets_dir: Path) -> list[str]:
    """Check a single chart for domain mismatches. Returns list of issues."""
    issues = []

    try:
        with open(chart_path, 'r', encoding='utf-8') as f:
            chart = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        return [f"Could not read chart: {e}"]

    # Get CSV path from chart
    data_url = chart.get('data', {}).get('url', '')
    if not data_url:
        return []  # No data URL

    # Convert URL to file path
    csv_filename = data_url.lstrip('/')
    csv_path = datasets_dir / csv_filename.replace('datasets/', '')

    if not csv_path.exists():
        # Try alternate path structure
        csv_path = datasets_dir.parent / 'public' / csv_filename

    if not csv_path.exists():
        return [f"CSV not found: {csv_filename}"]

    # Get color encoding
    color_encoding = extract_color_encoding(chart)
    if not color_encoding:
        return []  # No color encoding

    field = color_encoding.get('field')
    scale = color_encoding.get('scale', {})
    domain = scale.get('domain', [])

    if not field or not domain:
        return []  # No explicit domain to check

    # Get actual values from CSV
    csv_values = get_csv_unique_values(csv_path, field)

    if not csv_values:
        return [f"Could not read field '{field}' from CSV"]

    # Check for mismatches
    domain_set = set(domain)

    # Values in domain but not in CSV
    missing_in_csv = domain_set - csv_values
    if missing_in_csv:
        issues.append(
            f"Domain values NOT in CSV: {sorted(missing_in_csv)}\n"
            f"         CSV values: {sorted(csv_values)}\n"
            f"         Field: '{field}'"
        )

    # Values in CSV but not in domain (less critical, but worth noting)
    missing_in_domain = csv_values - domain_set
    if missing_in_domain and not missing_in_csv:
        # Only report if there are no critical issues
        issues.append(
            f"CSV values NOT in domain: {sorted(missing_in_domain)}\n"
            f"         (Chart may not show all categories)"
        )

    return issues


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Check charts for domain/CSV mismatches")
    parser.add_argument("--charts-dir", type=str,
                        default="/Users/ritz/Insync/robert@aum.edu.mn/Google Drive/data/data.mn/public/charts",
                        help="Directory containing chart JSON files")
    parser.add_argument("--datasets-dir", type=str,
                        default="/Users/ritz/Insync/robert@aum.edu.mn/Google Drive/data/data.mn/public/datasets",
                        help="Directory containing CSV files")
    args = parser.parse_args()

    charts_dir = Path(args.charts_dir)
    datasets_dir = Path(args.datasets_dir)

    if not charts_dir.exists():
        print(f"Error: Charts directory not found: {charts_dir}")
        return 1

    chart_files = sorted(charts_dir.glob("*.json"))
    print(f"Checking {len(chart_files)} charts for domain mismatches...\n")

    charts_with_issues = 0
    charts_ok = 0

    for chart_path in chart_files:
        issues = check_chart(chart_path, datasets_dir)

        if issues:
            # Check if any are critical (domain values not in CSV)
            critical = any("NOT in CSV" in issue and "Domain values" in issue for issue in issues)

            if critical:
                print(f"❌ {chart_path.name}")
                charts_with_issues += 1
            else:
                print(f"⚠️  {chart_path.name}")
                charts_ok += 1

            for issue in issues:
                for line in issue.split('\n'):
                    print(f"   {line}")
            print()
        else:
            charts_ok += 1

    print("=" * 50)
    print(f"✓ {charts_ok} charts OK")
    if charts_with_issues > 0:
        print(f"❌ {charts_with_issues} charts with CRITICAL domain mismatches")
        return 1
    else:
        print("No critical domain mismatches found!")

    return 0


if __name__ == "__main__":
    exit(main())
