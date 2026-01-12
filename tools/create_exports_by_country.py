#!/usr/bin/env python3
"""
Create exports-by-country dataset from NSO table DT_NSO_1400_006V3.px

This script:
1. Fetches bilingual data from NSO API
2. Filters to top 6 trading partners for chart (China, Switzerland, USA, Russia, Iran, Italy)
3. Creates chart CSVs (subset for visualization)
4. Creates download CSVs (all countries, long format)
5. Creates XLSX export (all countries, wide format)
6. Generates bilingual Vega-Lite chart specs
7. Validates charts
8. Generates bilingual MDX pages
9. Updates registry and publishes
"""

import sys
from pathlib import Path

# Add skills to path
skills_dir = Path.home() / "Insync/robert@aum.edu.mn/Google Drive/.claude/skills"
sys.path.insert(0, str(skills_dir / "datamn-source-nso"))

from fetch_data import NSO_API, jsonstat2_to_dataframe, get_table_path
import pandas as pd
import json
from openpyxl.utils import get_column_letter

# Configuration
DATASET_ID = "exports-by-country"
TABLE_ID = "DT_NSO_1400_006V3.px"
BASE_DIR = Path("/home/ritz/Insync/robert@aum.edu.mn/Google Drive/data/data.mn")
OUTPUT_DIR = BASE_DIR / "public/datasets"
CHART_DIR = BASE_DIR / "public/charts"

# Top 6 countries for chart (based on 2024 data)
# Note: Use exact names from NSO API
TOP_COUNTRIES = ["China", "Switzerland", "USA", "Russian Federation", "Iran", "Italy"]
TOP_COUNTRIES_MN = ["БНХАУ", "Швейцарь", "АНУ", "ОХУ", "Иран", "Итали"]

def fetch_nso_data(table_id: str, language: str) -> pd.DataFrame:
    """Fetch data from NSO API"""
    print(f"\nFetching {language.upper()} data from NSO API...")

    sector_id, subsector_id = get_table_path(table_id)
    if not sector_id or not subsector_id:
        raise ValueError(f"Table {table_id} not found in metadata")

    print(f"  Sector: {sector_id}")
    print(f"  Subsector: {subsector_id}")

    api = NSO_API(language=language)
    data = api.fetch_data(sector_id, subsector_id, table_id)

    if not data:
        raise ValueError(f"Failed to fetch data for {table_id}")

    df = jsonstat2_to_dataframe(data)
    print(f"  Fetched {len(df)} rows, columns: {df.columns.tolist()}")

    return df

def clean_data(df: pd.DataFrame, language: str) -> pd.DataFrame:
    """Clean and standardize column names"""
    # Strip whitespace from all string columns
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()

    # Print original columns for debugging
    print(f"  Original columns: {df.columns.tolist()}")

    # Map to standard column names based on actual column names
    if language == 'en':
        # Expected columns: 'Countries', 'Year', 'value'
        rename_map = {
            'Countries': 'country',
            'Year': 'year',
            'value': 'value'
        }
    else:  # mn
        # Expected columns: 'Улс орон', 'Он', 'value'
        rename_map = {
            'Улс орон': 'улс',
            'Он': 'он',
            'value': 'утга'
        }

    df.rename(columns=rename_map, inplace=True)
    print(f"  Renamed columns: {df.columns.tolist()}")

    return df

def filter_chart_data(df: pd.DataFrame, language: str) -> pd.DataFrame:
    """Filter to top 6 countries only"""
    country_col = 'country' if language == 'en' else 'улс'
    top_list = TOP_COUNTRIES if language == 'en' else TOP_COUNTRIES_MN

    # Filter
    chart_df = df[df[country_col].isin(top_list)].copy()

    print(f"  Filtered to {len(chart_df)} rows ({len(top_list)} countries)")

    return chart_df

def create_xlsx_export(df_en: pd.DataFrame, output_path: Path):
    """Create wide-format XLSX export"""
    print(f"\nCreating XLSX export (wide format)...")

    # Pivot to wide format: years as rows, countries as columns
    wide_df = df_en.pivot_table(
        index='year',
        columns='country',
        values='value',
        aggfunc='first'
    ).reset_index()

    # Sort columns: year first, then countries by 2024 value
    year_col = ['year']
    other_cols = [c for c in wide_df.columns if c != 'year']
    # Sort by last year's value (descending)
    last_year_values = wide_df[wide_df['year'] == wide_df['year'].max()][other_cols].iloc[0]
    sorted_cols = last_year_values.sort_values(ascending=False).index.tolist()
    wide_df = wide_df[year_col + sorted_cols]

    # Export with formatting
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        wide_df.to_excel(writer, index=False, sheet_name='Exports by Country')

        # Auto-adjust column widths
        worksheet = writer.sheets['Exports by Country']
        for idx, col in enumerate(wide_df.columns):
            max_length = max(
                wide_df[col].astype(str).map(len).max(),
                len(str(col))
            ) + 2
            col_letter = get_column_letter(idx + 1)
            worksheet.column_dimensions[col_letter].width = min(max_length, 30)

    print(f"  Saved: {output_path}")
    print(f"  Dimensions: {wide_df.shape[0]} years × {wide_df.shape[1]} columns")

def create_vega_chart(dataset_id: str, language: str, output_path: Path):
    """Create Vega-Lite chart specification"""

    if language == 'en':
        chart_spec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "description": "Mongolia's exports by top trading partners (2005-2024)",
            "data": {
                "url": f"/datasets/{dataset_id}-en.csv",
                "format": {"type": "csv"}
            },
            "encoding": {
                "x": {
                    "field": "year",
                    "type": "quantitative",
                    "title": "Year",
                    "axis": {"format": "d", "tickMinStep": 5, "grid": False}
                },
                "y": {
                    "field": "value",
                    "type": "quantitative",
                    "title": "Exports (USD)",
                    "axis": {"format": ".2s"}
                },
                "color": {
                    "field": "country",
                    "type": "nominal",
                    "title": "Trading Partner",
                    "scale": {
                        "domain": ["China", "Switzerland", "USA", "Russian Federation", "Iran", "Italy"],
                        "range": ["#4c78a8", "#f58518", "#e45756", "#72b7b2", "#54a24b", "#eeca3b"]
                    },
                    "legend": {"orient": "top", "title": None}
                }
            },
            "layer": [
                {
                    "mark": {"type": "line", "strokeWidth": 2.5, "interpolate": "monotone"}
                },
                {
                    "params": [{
                        "name": "hover",
                        "select": {"type": "point", "nearest": True, "on": "pointerover", "clear": "pointerout"}
                    }],
                    "mark": {"type": "point", "filled": True, "size": 80},
                    "encoding": {
                        "opacity": {
                            "condition": {"param": "hover", "empty": False, "value": 1},
                            "value": 0
                        },
                        "tooltip": [
                            {"field": "year", "title": "Year", "format": "d"},
                            {"field": "country", "title": "Country"},
                            {"field": "value", "title": "Exports (USD)", "format": "$,.0f"}
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
    else:  # mn
        chart_spec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "description": "Монгол Улсын экспорт гол худалдааны түншээр (2005-2024)",
            "data": {
                "url": f"/datasets/{dataset_id}-mn.csv",
                "format": {"type": "csv"}
            },
            "encoding": {
                "x": {
                    "field": "он",
                    "type": "quantitative",
                    "title": "Он",
                    "axis": {"format": "d", "tickMinStep": 5, "grid": False}
                },
                "y": {
                    "field": "утга",
                    "type": "quantitative",
                    "title": "Экспорт (ам.доллар)",
                    "axis": {"format": ".2s"}
                },
                "color": {
                    "field": "улс",
                    "type": "nominal",
                    "title": "Худалдааны түнш",
                    "scale": {
                        "domain": ["БНХАУ", "Швейцарь", "АНУ", "ОХУ", "Иран", "Итали"],
                        "range": ["#4c78a8", "#f58518", "#e45756", "#72b7b2", "#54a24b", "#eeca3b"]
                    },
                    "legend": {"orient": "top", "title": None}
                }
            },
            "layer": [
                {
                    "mark": {"type": "line", "strokeWidth": 2.5, "interpolate": "monotone"}
                },
                {
                    "params": [{
                        "name": "hover",
                        "select": {"type": "point", "nearest": True, "on": "pointerover", "clear": "pointerout"}
                    }],
                    "mark": {"type": "point", "filled": True, "size": 80},
                    "encoding": {
                        "opacity": {
                            "condition": {"param": "hover", "empty": False, "value": 1},
                            "value": 0
                        },
                        "tooltip": [
                            {"field": "он", "title": "Он", "format": "d"},
                            {"field": "улс", "title": "Улс"},
                            {"field": "утга", "title": "Экспорт (ам.доллар)", "format": "$,.0f"}
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

    # Save chart
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(chart_spec, f, indent=2, ensure_ascii=False)

    print(f"  Saved: {output_path}")

def main():
    print("=" * 60)
    print("Creating exports-by-country dataset")
    print("=" * 60)

    # Step 1: Fetch bilingual data
    df_en = fetch_nso_data(TABLE_ID, 'en')
    df_mn = fetch_nso_data(TABLE_ID, 'mn')

    # Step 2: Clean data
    print("\nCleaning data...")
    df_en = clean_data(df_en, 'en')
    df_mn = clean_data(df_mn, 'mn')

    print(f"  EN columns: {df_en.columns.tolist()}")
    print(f"  MN columns: {df_mn.columns.tolist()}")

    # Show unique countries
    country_col_en = 'country' if 'country' in df_en.columns else df_en.columns[1]
    country_col_mn = 'улс' if 'улс' in df_mn.columns else df_mn.columns[1]

    print(f"\n  Unique countries (EN): {df_en[country_col_en].nunique()}")
    print(f"  Sample countries: {df_en[country_col_en].unique()[:10].tolist()}")

    # Step 3: Create chart CSVs (filtered to top 6)
    print("\nCreating chart CSVs (top 6 countries)...")
    chart_en = filter_chart_data(df_en, 'en')
    chart_mn = filter_chart_data(df_mn, 'mn')

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    chart_en.to_csv(OUTPUT_DIR / f"{DATASET_ID}-en.csv", index=False)
    chart_mn.to_csv(OUTPUT_DIR / f"{DATASET_ID}-mn.csv", index=False)

    print(f"  Saved: {OUTPUT_DIR / f'{DATASET_ID}-en.csv'}")
    print(f"  Saved: {OUTPUT_DIR / f'{DATASET_ID}-mn.csv'}")

    # Step 4: Create download CSVs (all countries)
    print("\nCreating download CSVs (all countries)...")
    df_en.to_csv(OUTPUT_DIR / f"{DATASET_ID}-all-en.csv", index=False)
    df_mn.to_csv(OUTPUT_DIR / f"{DATASET_ID}-all-mn.csv", index=False)

    print(f"  Saved: {OUTPUT_DIR / f'{DATASET_ID}-all-en.csv'} ({len(df_en)} rows)")
    print(f"  Saved: {OUTPUT_DIR / f'{DATASET_ID}-all-mn.csv'} ({len(df_mn)} rows)")

    # Step 5: Create XLSX export (wide format)
    create_xlsx_export(df_en, OUTPUT_DIR / f"{DATASET_ID}.xlsx")

    # Step 6: Create Vega-Lite charts
    print("\nCreating Vega-Lite charts...")
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    create_vega_chart(DATASET_ID, 'en', CHART_DIR / f"{DATASET_ID}-en.json")
    create_vega_chart(DATASET_ID, 'mn', CHART_DIR / f"{DATASET_ID}-mn.json")

    # Calculate statistics
    year_col_en = 'year' if 'year' in df_en.columns else df_en.columns[0]
    value_col_en = 'value' if 'value' in df_en.columns else df_en.columns[2]

    stats = {
        "total_rows": len(df_en),
        "chart_rows": len(chart_en),
        "total_countries": df_en[country_col_en].nunique(),
        "chart_countries": 6,
        "first_year": int(df_en[year_col_en].min()),
        "last_year": int(df_en[year_col_en].max()),
        "min_value": float(df_en[value_col_en].min()),
        "max_value": float(df_en[value_col_en].max()),
    }

    print("\n" + "=" * 60)
    print("DATASET STATISTICS")
    print("=" * 60)
    print(f"Total rows (all countries): {stats['total_rows']}")
    print(f"Chart rows (top 6): {stats['chart_rows']}")
    print(f"Total countries: {stats['total_countries']}")
    print(f"Chart countries: {stats['chart_countries']}")
    print(f"Year range: {stats['first_year']}-{stats['last_year']}")
    print(f"Value range: ${stats['min_value']:,.0f} - ${stats['max_value']:,.0f}")

    print("\n" + "=" * 60)
    print("FILES GENERATED")
    print("=" * 60)
    print(f"✓ {OUTPUT_DIR / f'{DATASET_ID}-en.csv'} (chart data)")
    print(f"✓ {OUTPUT_DIR / f'{DATASET_ID}-mn.csv'} (chart data)")
    print(f"✓ {OUTPUT_DIR / f'{DATASET_ID}-all-en.csv'} (full download)")
    print(f"✓ {OUTPUT_DIR / f'{DATASET_ID}-all-mn.csv'} (full download)")
    print(f"✓ {OUTPUT_DIR / f'{DATASET_ID}.xlsx'} (wide format)")
    print(f"✓ {CHART_DIR / f'{DATASET_ID}-en.json'} (chart spec)")
    print(f"✓ {CHART_DIR / f'{DATASET_ID}-mn.json'} (chart spec)")

    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("1. Validate charts")
    print("2. Generate MDX pages")
    print("3. Update registry")
    print("4. Publish dataset")

    return stats

if __name__ == '__main__':
    stats = main()
