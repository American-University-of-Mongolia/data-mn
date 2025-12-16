#!/usr/bin/env python3
"""
Create household income datasets from NSO table DT_NSO_1900_001V1.px
"""

import pandas as pd
import json
import os
from pathlib import Path

# Paths
BASE_DIR = Path("/Users/ritz/Insync/robert@aum.edu.mn/Google Drive/data")
SOURCE_DIR = BASE_DIR / "data.mn/src/data/datasets"
OUTPUT_DIR = BASE_DIR / "data.mn/public/datasets"
CHART_DIR = BASE_DIR / "data.mn/public/charts"

# Create output directories
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)

# Load English and Mongolian data
df_en = pd.read_csv(SOURCE_DIR / "nso-1900-001v1-en.csv")
df_mn = pd.read_csv(SOURCE_DIR / "nso-1900-001v1-mn.csv")

# Strip leading/trailing spaces from all string columns
df_en = df_en.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
df_mn = df_mn.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

print(f"Loaded English data: {len(df_en)} rows")
print(f"Loaded Mongolian data: {len(df_mn)} rows")
print(f"\nEnglish columns: {df_en.columns.tolist()}")
print(f"Mongolian columns: {df_mn.columns.tolist()}")
print(f"\nEnglish Location values: {df_en['Location'].unique()}")
print(f"English Income types: {df_en['Types of income'].unique()}")

# ============================================
# Dataset 1: household-income-total
# ============================================
print("\n" + "="*60)
print("Creating: household-income-total")
print("="*60)

# Filter: National average + Total income
df1_en = df_en[
    (df_en['Location'] == 'National average') &
    (df_en['Types of income'] == 'Total income')
].copy()

df1_mn = df_mn[
    (df_mn['Байршил'] == 'Улсын дундаж') &
    (df_mn['Орлогын төрөл'] == 'Нийт орлого')
].copy()

# Clean columns
df1_en = df1_en[['Year', 'value']].rename(columns={'Year': 'year'})
df1_mn = df1_mn[['Он', 'value']].rename(columns={'Он': 'year'})

# Sort by year
df1_en = df1_en.sort_values('year')
df1_mn = df1_mn.sort_values('year')

print(f"Filtered to {len(df1_en)} rows")
print(f"Year range: {df1_en['year'].min()} - {df1_en['year'].max()}")
print(f"Value range: {df1_en['value'].min():,.0f} - {df1_en['value'].max():,.0f} MNT")

# Save CSVs
df1_en.to_csv(OUTPUT_DIR / "household-income-total-en.csv", index=False)
df1_mn.to_csv(OUTPUT_DIR / "household-income-total-mn.csv", index=False)

# Save XLSX (English version)
with pd.ExcelWriter(OUTPUT_DIR / "household-income-total-en.xlsx", engine='openpyxl') as writer:
    df1_en.to_excel(writer, index=False, sheet_name='Data')

# Save XLSX (Mongolian version)
with pd.ExcelWriter(OUTPUT_DIR / "household-income-total-mn.xlsx", engine='openpyxl') as writer:
    df1_mn.to_excel(writer, index=False, sheet_name='Data')

# Create Vega-Lite chart (area chart)
chart1_en = {
    "data": {"url": "/datasets/household-income-total-en.csv"},
    "mark": {"type": "area", "line": True, "point": True},
    "encoding": {
        "x": {
            "field": "year",
            "type": "quantitative",
            "axis": {"title": "Year", "format": "d"}
        },
        "y": {
            "field": "value",
            "type": "quantitative",
            "axis": {"title": "Monthly Income (MNT)", "format": ",.0f"}
        },
        "tooltip": [
            {"field": "year", "type": "quantitative", "title": "Year", "format": "d"},
            {"field": "value", "type": "quantitative", "title": "Income (MNT)", "format": ",.0f"}
        ]
    }
}

chart1_mn = {
    "data": {"url": "/datasets/household-income-total-mn.csv"},
    "mark": {"type": "area", "line": True, "point": True},
    "encoding": {
        "x": {
            "field": "year",
            "type": "quantitative",
            "axis": {"title": "Он", "format": "d"}
        },
        "y": {
            "field": "value",
            "type": "quantitative",
            "axis": {"title": "Сарын орлого (₮)", "format": ",.0f"}
        },
        "tooltip": [
            {"field": "year", "type": "quantitative", "title": "Он", "format": "d"},
            {"field": "value", "type": "quantitative", "title": "Орлого (₮)", "format": ",.0f"}
        ]
    }
}

with open(CHART_DIR / "household-income-total-en.json", 'w') as f:
    json.dump(chart1_en, f, indent=2)

with open(CHART_DIR / "household-income-total-mn.json", 'w') as f:
    json.dump(chart1_mn, f, indent=2)

print("✓ Created household-income-total files")

# ============================================
# Dataset 2: household-income-by-location
# ============================================
print("\n" + "="*60)
print("Creating: household-income-by-location")
print("="*60)

# Filter: Urban and Rural, Total income
df2_en = df_en[
    (df_en['Location'].isin(['Urban', 'Rural'])) &
    (df_en['Types of income'] == 'Total income')
].copy()

df2_mn = df_mn[
    (df_mn['Байршил'].isin(['Хот', 'Хөдөө'])) &
    (df_mn['Орлогын төрөл'] == 'Нийт орлого')
].copy()

# Clean columns
df2_en = df2_en[['Location', 'Year', 'value']].rename(columns={'Location': 'location', 'Year': 'year'})
df2_mn = df2_mn[['Байршил', 'Он', 'value']].rename(columns={'Байршил': 'location', 'Он': 'year'})

# Sort by year and location
df2_en = df2_en.sort_values(['year', 'location'])
df2_mn = df2_mn.sort_values(['year', 'location'])

print(f"Filtered to {len(df2_en)} rows")
print(f"Year range: {df2_en['year'].min()} - {df2_en['year'].max()}")
print(f"Locations: {df2_en['location'].unique()}")

# Save CSVs
df2_en.to_csv(OUTPUT_DIR / "household-income-by-location-en.csv", index=False)
df2_mn.to_csv(OUTPUT_DIR / "household-income-by-location-mn.csv", index=False)

# Save XLSX (English version)
with pd.ExcelWriter(OUTPUT_DIR / "household-income-by-location-en.xlsx", engine='openpyxl') as writer:
    df2_en.to_excel(writer, index=False, sheet_name='Data')

# Save XLSX (Mongolian version)
with pd.ExcelWriter(OUTPUT_DIR / "household-income-by-location-mn.xlsx", engine='openpyxl') as writer:
    df2_mn.to_excel(writer, index=False, sheet_name='Data')

# Create Vega-Lite chart (multi-line)
chart2_en = {
    "data": {"url": "/datasets/household-income-by-location-en.csv"},
    "mark": {"type": "line", "point": True},
    "encoding": {
        "x": {
            "field": "year",
            "type": "quantitative",
            "axis": {"title": "Year", "format": "d"}
        },
        "y": {
            "field": "value",
            "type": "quantitative",
            "axis": {"title": "Monthly Income (MNT)", "format": ",.0f"}
        },
        "color": {
            "field": "location",
            "type": "nominal",
            "legend": {"title": "Location"}
        },
        "tooltip": [
            {"field": "year", "type": "quantitative", "title": "Year", "format": "d"},
            {"field": "location", "type": "nominal", "title": "Location"},
            {"field": "value", "type": "quantitative", "title": "Income (MNT)", "format": ",.0f"}
        ]
    }
}

chart2_mn = {
    "data": {"url": "/datasets/household-income-by-location-mn.csv"},
    "mark": {"type": "line", "point": True},
    "encoding": {
        "x": {
            "field": "year",
            "type": "quantitative",
            "axis": {"title": "Он", "format": "d"}
        },
        "y": {
            "field": "value",
            "type": "quantitative",
            "axis": {"title": "Сарын орлого (₮)", "format": ",.0f"}
        },
        "color": {
            "field": "location",
            "type": "nominal",
            "legend": {"title": "Байршил"}
        },
        "tooltip": [
            {"field": "year", "type": "quantitative", "title": "Он", "format": "d"},
            {"field": "location", "type": "nominal", "title": "Байршил"},
            {"field": "value", "type": "quantitative", "title": "Орлого (₮)", "format": ",.0f"}
        ]
    }
}

with open(CHART_DIR / "household-income-by-location-en.json", 'w') as f:
    json.dump(chart2_en, f, indent=2)

with open(CHART_DIR / "household-income-by-location-mn.json", 'w') as f:
    json.dump(chart2_mn, f, indent=2)

print("✓ Created household-income-by-location files")

# ============================================
# Summary
# ============================================
print("\n" + "="*60)
print("SUMMARY")
print("="*60)

files_created = [
    "household-income-total-en.csv",
    "household-income-total-mn.csv",
    "household-income-total-en.xlsx",
    "household-income-total-mn.xlsx",
    "household-income-total-en.json (chart)",
    "household-income-total-mn.json (chart)",
    "household-income-by-location-en.csv",
    "household-income-by-location-mn.csv",
    "household-income-by-location-en.xlsx",
    "household-income-by-location-mn.xlsx",
    "household-income-by-location-en.json (chart)",
    "household-income-by-location-mn.json (chart)",
]

for f in files_created:
    print(f"  ✓ {f}")

print("\nDataset Statistics:")
print(f"  household-income-total: {len(df1_en)} rows ({df1_en['year'].min()}-{df1_en['year'].max()})")
print(f"  household-income-by-location: {len(df2_en)} rows ({df2_en['year'].min()}-{df2_en['year'].max()})")
