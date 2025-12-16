#!/usr/bin/env python3
"""
Process population-by-age-sex.csv into separate datasets with CSV and XLSX formats.
"""

import pandas as pd
from pathlib import Path

# Paths
DATA_DIR = Path(__file__).parent.parent.parent / "data.mn" / "public" / "datasets"
SOURCE_FILE = DATA_DIR / "population-by-age-sex.csv"

def main():
    # Read source data
    df = pd.read_csv(SOURCE_FILE)
    print(f"Loaded {len(df)} rows from {SOURCE_FILE}")
    print(f"Columns: {df.columns.tolist()}")

    # Rename columns for easier handling
    df.columns = ['sex_code', 'sex', 'age_code', 'age', 'year_code', 'year', 'population']

    # 1. Total population over time
    total_pop = df[(df['sex'] == 'Total') & (df['age'] == 'Total')][['year', 'population']].copy()
    total_pop = total_pop.sort_values('year')
    save_dataset(total_pop, 'population-total', 'Total Population')

    # 2. Population by age group (pyramid) - latest year, by sex
    latest_year = df['year'].max()
    pyramid = df[
        (df['year'] == latest_year) &
        (df['age'] != 'Total') &
        (df['sex'] != 'Total')
    ][['sex', 'age', 'age_code', 'population']].copy()
    # Sort by age_code to get proper age ordering
    pyramid = pyramid.sort_values(['sex', 'age_code'])
    pyramid = pyramid[['sex', 'age', 'population']]
    save_dataset(pyramid, 'population-pyramid', f'Population Pyramid ({latest_year})')

    # 3. Population by sex over time
    by_sex = df[
        (df['age'] == 'Total') &
        (df['sex'] != 'Total')
    ][['year', 'sex', 'population']].copy()
    by_sex = by_sex.sort_values(['year', 'sex'])
    save_dataset(by_sex, 'population-by-sex', 'Population by Sex')

    print("\nDone! Created 3 datasets with CSV and XLSX formats.")

def save_dataset(df: pd.DataFrame, name: str, description: str):
    """Save dataset as both CSV and XLSX"""
    csv_path = DATA_DIR / f"{name}.csv"
    xlsx_path = DATA_DIR / f"{name}.xlsx"

    # Save CSV
    df.to_csv(csv_path, index=False)
    csv_size = csv_path.stat().st_size
    print(f"\n{description}:")
    print(f"  CSV: {csv_path.name} ({csv_size:,} bytes)")

    # Save XLSX
    df.to_excel(xlsx_path, index=False, sheet_name='Data')
    xlsx_size = xlsx_path.stat().st_size
    print(f"  XLSX: {xlsx_path.name} ({xlsx_size:,} bytes)")
    print(f"  Rows: {len(df)}")

if __name__ == "__main__":
    main()
