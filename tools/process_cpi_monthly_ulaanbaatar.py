#!/usr/bin/env python3
"""
Process CPI Monthly Ulaanbaatar dataset
Split from nso-cpi-ulaanbaatar-mom parent dataset
"""

import pandas as pd
import json
from pathlib import Path
from openpyxl.utils import get_column_letter

# Paths
BASE_DIR = Path("/home/ritz/Insync/robert@aum.edu.mn/Google Drive/data")
PARENT_DIR = BASE_DIR / "tools/versions/nso-cpi-ulaanbaatar-mom"
OUTPUT_DIR = BASE_DIR / "data.mn/public/datasets"
CHART_DIR = BASE_DIR / "data.mn/public/charts"

# Ensure output directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)

DATASET_ID = "cpi-monthly-ulaanbaatar"

# Step 1: Load parent data
print("Loading parent data...")
df_en = pd.read_csv(PARENT_DIR / "nso-0600-003v4-en.csv")
df_mn = pd.read_csv(PARENT_DIR / "nso-0600-003v4-mn.csv")

print(f"Loaded EN: {len(df_en)} rows")
print(f"Loaded MN: {len(df_mn)} rows")
print(f"EN columns: {df_en.columns.tolist()}")
print(f"EN unique reference years: {df_en['Reference year'].unique()}")
print(f"EN unique groups: {df_en['Group'].unique()[:5]}...")

# Step 2: Apply split filter
# Filter: Reference year = "2020=100", Group = "Overall index"
print("\nApplying split filter...")
df_en_filtered = df_en[
    (df_en['Reference year'] == '2020=100') &
    (df_en['Group'] == 'Overall index')
].copy()

df_mn_filtered = df_mn[
    (df_mn['Суурь он'] == '2020=100') &
    (df_mn['Бүлэг'] == 'Ерөнхий индекс')
].copy()

print(f"Filtered EN: {len(df_en_filtered)} rows")
print(f"Filtered MN: {len(df_mn_filtered)} rows")

# Step 3: Transform - keep only month and value columns
# Rename "Month" to "month"
df_en_clean = df_en_filtered[['Month', 'value']].copy()
df_en_clean.columns = ['month', 'value']

df_mn_clean = df_mn_filtered[['Сар', 'value']].copy()
df_mn_clean.columns = ['сар', 'утга']

# Strip whitespace from all string columns
for col in df_en_clean.select_dtypes(include=['object']).columns:
    df_en_clean[col] = df_en_clean[col].astype(str).str.strip()

for col in df_mn_clean.select_dtypes(include=['object']).columns:
    df_mn_clean[col] = df_mn_clean[col].astype(str).str.strip()

# Convert value to numeric
df_en_clean['value'] = pd.to_numeric(df_en_clean['value'], errors='coerce')
df_mn_clean['утга'] = pd.to_numeric(df_mn_clean['утга'], errors='coerce')

# Remove rows with missing values
df_en_clean = df_en_clean.dropna()
df_mn_clean = df_mn_clean.dropna()

# Sort by month
df_en_clean = df_en_clean.sort_values('month')
df_mn_clean = df_mn_clean.sort_values('сар')

print(f"\nCleaned EN: {len(df_en_clean)} rows")
print(f"Cleaned MN: {len(df_mn_clean)} rows")
print(f"\nDate range EN: {df_en_clean['month'].min()} to {df_en_clean['month'].max()}")
print(f"Date range MN: {df_mn_clean['сар'].min()} to {df_mn_clean['сар'].max()}")

# Step 4: Calculate statistics
stats = {
    'row_count': len(df_en_clean),
    'first_month': df_en_clean['month'].min(),
    'last_month': df_en_clean['month'].max(),
    'min_value': float(df_en_clean['value'].min()),
    'max_value': float(df_en_clean['value'].max()),
    'latest_value': float(df_en_clean.iloc[-1]['value']) if len(df_en_clean) > 0 else None,
    'latest_month': df_en_clean.iloc[-1]['month'] if len(df_en_clean) > 0 else None,
}

print("\nStatistics:")
print(json.dumps(stats, indent=2))

# Step 5: Export chart CSV files (ALL data for this single-series chart)
print("\nExporting chart CSV files...")
df_en_clean.to_csv(OUTPUT_DIR / f"{DATASET_ID}-en.csv", index=False)
df_mn_clean.to_csv(OUTPUT_DIR / f"{DATASET_ID}-mn.csv", index=False)

# Step 6: Export download CSV files (same as chart for this dataset)
print("Exporting download CSV files...")
df_en_clean.to_csv(OUTPUT_DIR / f"{DATASET_ID}-all-en.csv", index=False)
df_mn_clean.to_csv(OUTPUT_DIR / f"{DATASET_ID}-all-mn.csv", index=False)

# Step 7: Export XLSX file (wide format - just 2 columns, so already wide)
print("Exporting XLSX file...")
xlsx_path = OUTPUT_DIR / f"{DATASET_ID}.xlsx"
with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
    df_en_clean.to_excel(writer, index=False, sheet_name='Data')

    # Auto-adjust column widths
    worksheet = writer.sheets['Data']
    for idx, col in enumerate(df_en_clean.columns):
        max_length = max(
            df_en_clean[col].astype(str).map(len).max(),
            len(str(col))
        ) + 2
        col_letter = get_column_letter(idx + 1)
        worksheet.column_dimensions[col_letter].width = min(max_length, 30)

print(f"\nFiles generated:")
print(f"  - {OUTPUT_DIR / f'{DATASET_ID}-en.csv'}")
print(f"  - {OUTPUT_DIR / f'{DATASET_ID}-mn.csv'}")
print(f"  - {OUTPUT_DIR / f'{DATASET_ID}-all-en.csv'}")
print(f"  - {OUTPUT_DIR / f'{DATASET_ID}-all-mn.csv'}")
print(f"  - {OUTPUT_DIR / f'{DATASET_ID}.xlsx'}")

# Save stats to file for reference
stats_file = Path(__file__).parent / f"{DATASET_ID}_stats.json"
with open(stats_file, 'w') as f:
    json.dump(stats, f, indent=2)
print(f"  - {stats_file}")

print("\n✓ Data processing complete!")
