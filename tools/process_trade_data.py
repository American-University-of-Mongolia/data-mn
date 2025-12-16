#!/usr/bin/env python3
"""
Process NSO foreign trade data into two datasets:
1. trade-total - Total turnover only
2. trade-exports-imports - Exports and Imports
"""

import pandas as pd
import json
from pathlib import Path

# Base paths
base_dir = Path("/Users/ritz/Insync/robert@aum.edu.mn/Google Drive/data")
data_dir = base_dir / "data.mn" / "src" / "data" / "datasets"
public_dir = base_dir / "data.mn" / "public" / "datasets"
charts_dir = base_dir / "data.mn" / "public" / "charts"

# Create output directories if needed
public_dir.mkdir(parents=True, exist_ok=True)
charts_dir.mkdir(parents=True, exist_ok=True)

# Load source data
df_en = pd.read_csv(data_dir / "nso-1400-001v1-year-en.csv")
df_mn = pd.read_csv(data_dir / "nso-1400-001v1-year-mn.csv")

print(f"Loaded {len(df_en)} rows from English data")
print(f"Loaded {len(df_mn)} rows from Mongolian data")

# Clean column names
df_en.columns = ['indicator', 'year', 'value']
df_mn.columns = ['indicator', 'year', 'value']

# Strip whitespace from indicators
df_en['indicator'] = df_en['indicator'].str.strip()
df_mn['indicator'] = df_mn['indicator'].str.strip()

print("\nEnglish indicators:", df_en['indicator'].unique())
print("Mongolian indicators:", df_mn['indicator'].unique())

# === Dataset 1: trade-total ===
print("\n=== Creating trade-total dataset ===")

# Filter for Total turnover
total_en = df_en[df_en['indicator'] == 'Total turnover'].copy()
total_mn = df_mn[df_mn['indicator'] == 'Нийт эргэлт'].copy()

# Keep only year and value
total_en = total_en[['year', 'value']].sort_values('year')
total_mn = total_mn[['year', 'value']].sort_values('year')

# Save CSVs
total_en.to_csv(public_dir / "trade-total-en.csv", index=False)
total_mn.to_csv(public_dir / "trade-total-mn.csv", index=False)

print(f"Saved trade-total: {len(total_en)} rows")
print(f"Year range: {total_en['year'].min()} - {total_en['year'].max()}")
print(f"Value range: ${total_en['value'].min():.2f}M - ${total_en['value'].max():.2f}M")

# Create XLSX
with pd.ExcelWriter(public_dir / "trade-total-en.xlsx", engine='openpyxl') as writer:
    total_en.to_excel(writer, index=False, sheet_name='Data')

with pd.ExcelWriter(public_dir / "trade-total-mn.xlsx", engine='openpyxl') as writer:
    total_mn.to_excel(writer, index=False, sheet_name='Data')

# Create Vega-Lite chart
chart_spec = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Mongolia Total Foreign Trade (1924-2024)",
    "data": {"url": "/datasets/trade-total-en.csv"},
    "mark": {
        "type": "area",
        "line": True,
        "point": False,
        "color": "#3b82f6",
        "opacity": 0.7
    },
    "encoding": {
        "x": {
            "field": "year",
            "type": "quantitative",
            "axis": {"title": "Year", "format": "d"}
        },
        "y": {
            "field": "value",
            "type": "quantitative",
            "axis": {"title": "Million USD"}
        },
        "tooltip": [
            {"field": "year", "type": "quantitative", "title": "Year", "format": "d"},
            {"field": "value", "type": "quantitative", "title": "Million USD", "format": ",.2f"}
        ]
    }
}

with open(charts_dir / "trade-total.json", 'w') as f:
    json.dump(chart_spec, f, indent=2)

print("Created chart: trade-total.json")

# === Dataset 2: trade-exports-imports ===
print("\n=== Creating trade-exports-imports dataset ===")

# Filter for Exports and Imports
exports_imports_en = df_en[df_en['indicator'].isin(['Exports', 'Imports'])].copy()
exports_imports_mn = df_mn[df_mn['indicator'].isin(['Экспорт', 'Импорт'])].copy()

# Rename columns for clarity
exports_imports_en.columns = ['indicator', 'year', 'value']
exports_imports_mn.columns = ['indicator', 'year', 'value']

# Sort
exports_imports_en = exports_imports_en.sort_values(['year', 'indicator'])
exports_imports_mn = exports_imports_mn.sort_values(['year', 'indicator'])

# Save CSVs
exports_imports_en.to_csv(public_dir / "trade-exports-imports-en.csv", index=False)
exports_imports_mn.to_csv(public_dir / "trade-exports-imports-mn.csv", index=False)

print(f"Saved trade-exports-imports: {len(exports_imports_en)} rows")
print(f"Year range: {exports_imports_en['year'].min()} - {exports_imports_en['year'].max()}")
print(f"Indicators: {exports_imports_en['indicator'].unique()}")

# Create XLSX
with pd.ExcelWriter(public_dir / "trade-exports-imports-en.xlsx", engine='openpyxl') as writer:
    exports_imports_en.to_excel(writer, index=False, sheet_name='Data')

with pd.ExcelWriter(public_dir / "trade-exports-imports-mn.xlsx", engine='openpyxl') as writer:
    exports_imports_mn.to_excel(writer, index=False, sheet_name='Data')

# Create Vega-Lite chart (multi-line)
chart_spec = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Mongolia Exports and Imports (1924-2024)",
    "data": {"url": "/datasets/trade-exports-imports-en.csv"},
    "mark": {
        "type": "line",
        "point": False,
        "strokeWidth": 2
    },
    "encoding": {
        "x": {
            "field": "year",
            "type": "quantitative",
            "axis": {"title": "Year", "format": "d"}
        },
        "y": {
            "field": "value",
            "type": "quantitative",
            "axis": {"title": "Million USD"}
        },
        "color": {
            "field": "indicator",
            "type": "nominal",
            "scale": {
                "domain": ["Exports", "Imports"],
                "range": ["#10b981", "#ef4444"]
            },
            "legend": {"title": "Indicator"}
        },
        "tooltip": [
            {"field": "year", "type": "quantitative", "title": "Year", "format": "d"},
            {"field": "indicator", "type": "nominal", "title": "Indicator"},
            {"field": "value", "type": "quantitative", "title": "Million USD", "format": ",.2f"}
        ]
    }
}

with open(charts_dir / "trade-exports-imports.json", 'w') as f:
    json.dump(chart_spec, f, indent=2)

print("Created chart: trade-exports-imports.json")

# === Summary Statistics ===
print("\n=== Summary Statistics ===")

print("\ntrade-total:")
print(f"  Rows: {len(total_en)}")
print(f"  First year: {total_en['year'].min()}")
print(f"  Last year: {total_en['year'].max()}")
print(f"  Min value: ${total_en['value'].min():.2f}M")
print(f"  Max value: ${total_en['value'].max():.2f}M")
print(f"  Latest value (2024): ${total_en[total_en['year']==2024]['value'].values[0]:.2f}M")

print("\ntrade-exports-imports:")
print(f"  Rows: {len(exports_imports_en)}")
print(f"  First year: {exports_imports_en['year'].min()}")
print(f"  Last year: {exports_imports_en['year'].max()}")

exports_2024 = exports_imports_en[(exports_imports_en['year']==2024) & (exports_imports_en['indicator']=='Exports')]['value'].values[0]
imports_2024 = exports_imports_en[(exports_imports_en['year']==2024) & (exports_imports_en['indicator']=='Imports')]['value'].values[0]

print(f"  2024 Exports: ${exports_2024:.2f}M")
print(f"  2024 Imports: ${imports_2024:.2f}M")
print(f"  2024 Balance: ${exports_2024 - imports_2024:.2f}M")

print("\n=== Processing Complete ===")
