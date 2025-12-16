#!/usr/bin/env python3
"""
Process CPI Food dataset from parent nso-cpi-ulaanbaatar-mom
Split dataset: cpi-food-ulaanbaatar
"""

import pandas as pd
import json
from pathlib import Path

# Paths
BASE_DIR = Path("/home/ritz/Insync/robert@aum.edu.mn/Google Drive/data")
PARENT_DIR = BASE_DIR / "tools/versions/nso-cpi-ulaanbaatar-mom"
OUTPUT_DIR = BASE_DIR / "data.mn/public/datasets"
CHART_DIR = BASE_DIR / "data.mn/public/charts"

# Ensure output directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)

# Dataset parameters
DATASET_ID = "cpi-food-ulaanbaatar"
PARENT_ID = "nso-cpi-ulaanbaatar-mom"

# Filter criteria
REFERENCE_YEAR = "2020=100"
GROUP_EN = " Food and non-alcaholic beverages"  # Note: includes leading space and typo
GROUP_MN = "Хүнсний бараа, ундаа, ус"  # Actual group name in data

print("=" * 80)
print("Processing CPI Food Ulaanbaatar Dataset")
print("=" * 80)

# ============================================
# STEP 1: Load and Filter English Data
# ============================================
print("\n[Step 1] Loading English data...")
df_en = pd.read_csv(PARENT_DIR / "nso-0600-003v4-en.csv")
print(f"  Loaded {len(df_en)} rows")

# Apply filter
df_en_filtered = df_en[
    (df_en["Reference year"] == REFERENCE_YEAR) &
    (df_en["Group"] == GROUP_EN)
].copy()

print(f"  Filtered to {len(df_en_filtered)} rows")
print(f"  Date range: {df_en_filtered['Month'].min()} to {df_en_filtered['Month'].max()}")

# Clean up: rename columns, select only needed ones
df_en_filtered = df_en_filtered[["Month", "value"]].copy()
df_en_filtered.columns = ["month", "value"]

# Strip whitespace from all string columns
for col in df_en_filtered.select_dtypes(include=['object']).columns:
    df_en_filtered[col] = df_en_filtered[col].astype(str).str.strip()

# Convert value to numeric (in case it's string)
df_en_filtered["value"] = pd.to_numeric(df_en_filtered["value"], errors='coerce')

# Sort by month
df_en_filtered = df_en_filtered.sort_values("month").reset_index(drop=True)

print(f"  Final columns: {list(df_en_filtered.columns)}")
print(f"  Sample data:\n{df_en_filtered.head()}")

# ============================================
# STEP 2: Load and Filter Mongolian Data
# ============================================
print("\n[Step 2] Loading Mongolian data...")
df_mn = pd.read_csv(PARENT_DIR / "nso-0600-003v4-mn.csv")
print(f"  Loaded {len(df_mn)} rows")

# Apply filter (Mongolian column names)
df_mn_filtered = df_mn[
    (df_mn["Суурь он"] == REFERENCE_YEAR) &
    (df_mn["Бүлэг"] == GROUP_MN)
].copy()

print(f"  Filtered to {len(df_mn_filtered)} rows")

# Rename columns to Mongolian
df_mn_filtered = df_mn_filtered[["Сар", "value"]].copy()
df_mn_filtered.columns = ["сар", "утга"]

# Strip whitespace
for col in df_mn_filtered.select_dtypes(include=['object']).columns:
    df_mn_filtered[col] = df_mn_filtered[col].astype(str).str.strip()

# Convert value to numeric
df_mn_filtered["утга"] = pd.to_numeric(df_mn_filtered["утга"], errors='coerce')

# Sort by month
df_mn_filtered = df_mn_filtered.sort_values("сар").reset_index(drop=True)

print(f"  Sample data:\n{df_mn_filtered.head()}")

# ============================================
# STEP 3: Calculate Statistics
# ============================================
print("\n[Step 3] Calculating statistics...")

# Remove rows with NaN values
df_en_clean = df_en_filtered.dropna()
df_mn_clean = df_mn_filtered.dropna()

stats = {
    "row_count": len(df_en_clean),
    "first_month": df_en_clean["month"].min(),
    "last_month": df_en_clean["month"].max(),
    "min_value": float(df_en_clean["value"].min()),
    "max_value": float(df_en_clean["value"].max()),
    "latest_value": float(df_en_clean.iloc[-1]["value"]),
    "latest_month": df_en_clean.iloc[-1]["month"],
}

print(f"  Total rows: {stats['row_count']}")
print(f"  Date range: {stats['first_month']} to {stats['last_month']}")
print(f"  Value range: {stats['min_value']:.2f}% to {stats['max_value']:.2f}%")
print(f"  Latest ({stats['latest_month']}): {stats['latest_value']:.1f}%")

# ============================================
# STEP 4: Export CSV Files
# ============================================
print("\n[Step 4] Exporting CSV files...")

# Chart CSV (same as download for this dataset - it's already simple time series)
csv_en_path = OUTPUT_DIR / f"{DATASET_ID}-en.csv"
csv_mn_path = OUTPUT_DIR / f"{DATASET_ID}-mn.csv"

df_en_clean.to_csv(csv_en_path, index=False)
df_mn_clean.to_csv(csv_mn_path, index=False)

print(f"  ✓ {csv_en_path}")
print(f"  ✓ {csv_mn_path}")

# ============================================
# STEP 5: Export XLSX (Wide Format)
# ============================================
print("\n[Step 5] Exporting XLSX file...")

from openpyxl.utils import get_column_letter

# For this simple time series, wide format is just month + value
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

print(f"  ✓ {xlsx_path}")

# ============================================
# STEP 6: Generate Chart Specs
# ============================================
print("\n[Step 6] Generating Vega-Lite chart specifications...")

# English chart
chart_en = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Food price month-over-month change in Ulaanbaatar (2020=100 base)",
    "data": {
        "url": f"/datasets/{DATASET_ID}-en.csv",
        "format": {"type": "csv"}
    },
    "encoding": {
        "x": {
            "field": "month",
            "type": "temporal",
            "title": "Month",
            "axis": {"format": "%Y-%m", "grid": False}
        },
        "y": {
            "field": "value",
            "type": "quantitative",
            "title": "Food Price Change (%)",
            "axis": {"format": ".1f"}
        }
    },
    "layer": [
        {
            "mark": {
                "type": "area",
                "line": {"color": "#f58518", "strokeWidth": 2.5},
                "color": {
                    "x1": 1, "y1": 1, "x2": 1, "y2": 0,
                    "gradient": "linear",
                    "stops": [
                        {"offset": 0, "color": "rgba(245, 133, 24, 0.01)"},
                        {"offset": 1, "color": "rgba(245, 133, 24, 0.3)"}
                    ]
                },
                "interpolate": "monotone"
            }
        },
        {
            "params": [{
                "name": "hover",
                "select": {
                    "type": "point",
                    "nearest": True,
                    "on": "pointerover",
                    "clear": "pointerout"
                }
            }],
            "mark": {"type": "point", "filled": True, "color": "#f58518", "size": 100},
            "encoding": {
                "opacity": {
                    "condition": {"param": "hover", "empty": False, "value": 1},
                    "value": 0
                },
                "tooltip": [
                    {"field": "month", "title": "Month", "type": "temporal", "format": "%Y-%m"},
                    {"field": "value", "title": "Change (%)", "format": ".1f"}
                ]
            }
        }
    ],
    "config": {
        "axis": {
            "labelFontSize": 14,
            "titleFontSize": 16,
            "labelColor": "#64748b",
            "titleColor": "#334155"
        },
        "view": {"stroke": "transparent"},
        "legend": {"labelFontSize": 13, "titleFontSize": 14}
    }
}

# Mongolian chart
chart_mn = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "description": "Улаанбаатар хотын хүнсний үнийн сар бүрийн өөрчлөлт (2020=100 суурь)",
    "data": {
        "url": f"/datasets/{DATASET_ID}-mn.csv",
        "format": {"type": "csv"}
    },
    "encoding": {
        "x": {
            "field": "сар",
            "type": "temporal",
            "title": "Сар",
            "axis": {"format": "%Y-%m", "grid": False}
        },
        "y": {
            "field": "утга",
            "type": "quantitative",
            "title": "Хүнсний үнийн өөрчлөлт (%)",
            "axis": {"format": ".1f"}
        }
    },
    "layer": [
        {
            "mark": {
                "type": "area",
                "line": {"color": "#f58518", "strokeWidth": 2.5},
                "color": {
                    "x1": 1, "y1": 1, "x2": 1, "y2": 0,
                    "gradient": "linear",
                    "stops": [
                        {"offset": 0, "color": "rgba(245, 133, 24, 0.01)"},
                        {"offset": 1, "color": "rgba(245, 133, 24, 0.3)"}
                    ]
                },
                "interpolate": "monotone"
            }
        },
        {
            "params": [{
                "name": "hover",
                "select": {
                    "type": "point",
                    "nearest": True,
                    "on": "pointerover",
                    "clear": "pointerout"
                }
            }],
            "mark": {"type": "point", "filled": True, "color": "#f58518", "size": 100},
            "encoding": {
                "opacity": {
                    "condition": {"param": "hover", "empty": False, "value": 1},
                    "value": 0
                },
                "tooltip": [
                    {"field": "сар", "title": "Сар", "type": "temporal", "format": "%Y-%m"},
                    {"field": "утга", "title": "Өөрчлөлт (%)", "format": ".1f"}
                ]
            }
        }
    ],
    "config": {
        "axis": {
            "labelFontSize": 14,
            "titleFontSize": 16,
            "labelColor": "#64748b",
            "titleColor": "#334155"
        },
        "view": {"stroke": "transparent"},
        "legend": {"labelFontSize": 13, "titleFontSize": 14}
    }
}

# Save charts
chart_en_path = CHART_DIR / f"{DATASET_ID}-en.json"
chart_mn_path = CHART_DIR / f"{DATASET_ID}-mn.json"

with open(chart_en_path, 'w', encoding='utf-8') as f:
    json.dump(chart_en, f, indent=2, ensure_ascii=False)

with open(chart_mn_path, 'w', encoding='utf-8') as f:
    json.dump(chart_mn, f, indent=2, ensure_ascii=False)

print(f"  ✓ {chart_en_path}")
print(f"  ✓ {chart_mn_path}")

# ============================================
# STEP 7: Summary
# ============================================
print("\n" + "=" * 80)
print("PROCESSING COMPLETE")
print("=" * 80)
print(f"\nDataset ID: {DATASET_ID}")
print(f"Parent ID: {PARENT_ID}")
print(f"Row count: {stats['row_count']}")
print(f"Date range: {stats['first_month']} to {stats['last_month']}")
print(f"Latest value: {stats['latest_value']:.1f}% ({stats['latest_month']})")
print(f"\nFiles generated:")
print(f"  - {csv_en_path.name}")
print(f"  - {csv_mn_path.name}")
print(f"  - {xlsx_path.name}")
print(f"  - {chart_en_path.name}")
print(f"  - {chart_mn_path.name}")

# Export stats for next steps
stats_path = Path("/tmp/cpi_food_stats.json")
with open(stats_path, 'w') as f:
    json.dump(stats, f, indent=2)

print(f"\nStats saved to: {stats_path}")
print("\nNext steps:")
print("  1. Validate charts")
print("  2. Generate MDX pages")
print("  3. Validate all files")
print("  4. Update registry")
print("  5. Publish dataset")
