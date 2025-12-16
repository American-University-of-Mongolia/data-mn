#!/usr/bin/env python3
"""
Process inflation data from raw JSON to clean CSV
"""

import json
import pandas as pd
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR.parent.parent / "data.mn/public/datasets"
RAW_JSON = OUTPUT_DIR / "inflation-rate-raw.json"

def parse_jsonstat(jsonstat_data):
    """
    Parse JSON-stat2 format to DataFrame

    The data has dimensions:
    - Indicator (2 values): "end of year" and "average of year"
    - Year (34 values): 2024, 2023, ..., 1991

    Values are in row-major order: [indicator0_year0, indicator0_year1, ..., indicator1_year0, indicator1_year1, ...]
    """
    # Get dimensions
    indicator_labels = list(jsonstat_data['dimension']['Үзүүлэлт']['category']['label'].values())
    year_labels = list(jsonstat_data['dimension']['Он']['category']['label'].values())

    # Get values (flattened array)
    values = jsonstat_data['value']

    # Size tells us the shape: [2 indicators, 34 years]
    n_indicators = len(indicator_labels)
    n_years = len(year_labels)

    # Reconstruct the data
    rows = []
    idx = 0
    for i in range(n_indicators):
        for j in range(n_years):
            if idx < len(values) and values[idx] is not None:
                rows.append({
                    'indicator': indicator_labels[i],
                    'year': int(year_labels[j]),
                    'inflation_rate': values[idx]
                })
            idx += 1

    df = pd.DataFrame(rows)
    return df

def main():
    print("Processing inflation data...")

    # Load raw JSON
    with open(RAW_JSON, 'r') as f:
        data = json.load(f)

    # Parse to DataFrame
    df = parse_jsonstat(data)

    print(f"\nParsed {len(df)} rows")
    print(f"Indicators: {df['indicator'].unique()}")
    print(f"Year range: {df['year'].min()} - {df['year'].max()}")

    # Show both indicators
    print("\n" + "="*60)
    print("FULL DATA (Both Indicators)")
    print("="*60)
    print(df.head(20))

    # Create dataset with just "end of year" inflation rate
    print("\n" + "="*60)
    print("Creating inflation-rate dataset (end of year only)")
    print("="*60)

    df_eoy = df[df['indicator'] == 'Inflation rate, at the end of the year'].copy()
    df_eoy = df_eoy[['year', 'inflation_rate']].sort_values('year')

    print(f"\nFiltered to {len(df_eoy)} rows")
    print(f"Year range: {df_eoy['year'].min()} - {df_eoy['year'].max()}")
    print(f"Inflation range: {df_eoy['inflation_rate'].min()}% - {df_eoy['inflation_rate'].max()}%")

    print("\nFirst 10 rows:")
    print(df_eoy.head(10))

    print("\nLast 10 rows:")
    print(df_eoy.tail(10))

    # Save CSV
    csv_path = OUTPUT_DIR / "inflation-rate.csv"
    df_eoy.to_csv(csv_path, index=False)
    print(f"\nSaved CSV to: {csv_path}")

    # Save XLSX
    xlsx_path = OUTPUT_DIR / "inflation-rate.xlsx"
    with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
        df_eoy.to_excel(writer, index=False, sheet_name='Data')
    print(f"Saved XLSX to: {xlsx_path}")

    # Also save full data with both indicators for reference
    csv_full_path = OUTPUT_DIR / "inflation-rate-full.csv"
    df.to_csv(csv_full_path, index=False)
    print(f"\nSaved full dataset (both indicators) to: {csv_full_path}")

    print("\n" + "="*60)
    print("STATISTICS")
    print("="*60)
    print(f"Total years: {len(df_eoy)}")
    print(f"Year range: {df_eoy['year'].min()} - {df_eoy['year'].max()}")
    print(f"Latest year: {df_eoy['year'].max()}")
    print(f"Latest inflation rate: {df_eoy[df_eoy['year'] == df_eoy['year'].max()]['inflation_rate'].values[0]}%")
    print(f"Min inflation: {df_eoy['inflation_rate'].min()}%")
    print(f"Max inflation: {df_eoy['inflation_rate'].max()}%")
    print(f"Average inflation: {df_eoy['inflation_rate'].mean():.2f}%")

if __name__ == "__main__":
    main()
