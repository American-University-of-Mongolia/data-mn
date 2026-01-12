#!/usr/bin/env python3
"""
Transform imported vehicles data to create total vehicles dataset
Filters to top-level vehicle types only and sums by year
"""

import pandas as pd
from pathlib import Path
import sys

# Add tools directory to path for openpyxl
sys.path.insert(0, str(Path(__file__).parent))

def main():
    base_dir = Path("/Users/ritz/Library/CloudStorage/GoogleDrive-robert@aum.edu.mn/My Drive/data/data.mn")

    # Load raw data
    en_raw = pd.read_csv("/tmp/imported-vehicles-test/nso-1200-013v5-en.csv")
    mn_raw = pd.read_csv("/tmp/imported-vehicles-test/nso-1200-013v5-mn.csv")

    print(f"Loaded {len(en_raw)} rows from English raw data")
    print(f"Loaded {len(mn_raw)} rows from Mongolian raw data")

    # Filter to the three main vehicle types
    # Buses: "ten or more persons"
    # Passenger cars: "Motor cars and other motor vehicles principally"
    # Cargo trucks: "transport of goods"

    en_buses = en_raw[en_raw['Indicator'].str.contains('ten or more persons', case=False, na=False)].copy()
    en_cars = en_raw[en_raw['Indicator'].str.contains('Motor cars and other motor vehicles principally', case=False, na=False)].copy()
    en_trucks = en_raw[en_raw['Indicator'].str.contains('transport of goods', case=False, na=False)].copy()

    mn_buses = mn_raw[mn_raw['Үзүүлэлт'].str.contains('Нийтийн тээврийн', case=False, na=False)].copy()
    mn_cars = mn_raw[mn_raw['Үзүүлэлт'].str.contains('Суудлын автомашин', case=False, na=False)].copy()
    mn_trucks = mn_raw[mn_raw['Үзүүлэлт'].str.contains('Ачааны автомашин', case=False, na=False)].copy()

    print(f"EN - Buses: {len(en_buses)}, Cars: {len(en_cars)}, Trucks: {len(en_trucks)}")
    print(f"MN - Buses: {len(mn_buses)}, Cars: {len(mn_cars)}, Trucks: {len(mn_trucks)}")

    # Combine all three types
    en_filtered = pd.concat([en_buses, en_cars, en_trucks])
    mn_filtered = pd.concat([mn_buses, mn_cars, mn_trucks])

    print(f"After filtering to vehicle types: {len(en_filtered)} rows (EN), {len(mn_filtered)} rows (MN)")

    # Group by year and sum to get total vehicles
    en_total = en_filtered.groupby('Year')['value'].sum().reset_index()
    mn_total = mn_filtered.groupby('Он')['value'].sum().reset_index()

    # Rename columns to match standard format
    en_total.columns = ['year', 'value']
    mn_total.columns = ['он', 'утга']

    # Strip whitespace from all string columns
    for col in en_total.select_dtypes(include=['object']).columns:
        en_total[col] = en_total[col].astype(str).str.strip()
    for col in mn_total.select_dtypes(include=['object']).columns:
        mn_total[col] = mn_total[col].astype(str).str.strip()

    # Sort by year descending
    en_total = en_total.sort_values('year', ascending=False)
    mn_total = mn_total.sort_values('он', ascending=False)

    print(f"\nFinal dataset: {len(en_total)} years of data")
    print(f"Year range: {en_total['year'].min()} - {en_total['year'].max()}")
    print(f"Value range: {en_total['value'].min():.0f} - {en_total['value'].max():.0f}")

    # Create output directories
    datasets_dir = base_dir / "public" / "datasets"
    datasets_dir.mkdir(parents=True, exist_ok=True)

    # Export chart CSV files (same as full data for this simple dataset)
    en_chart_path = datasets_dir / "imported-vehicles-total-en.csv"
    mn_chart_path = datasets_dir / "imported-vehicles-total-mn.csv"

    en_total.to_csv(en_chart_path, index=False)
    mn_total.to_csv(mn_chart_path, index=False)
    print(f"\nChart CSV files created:")
    print(f"  {en_chart_path}")
    print(f"  {mn_chart_path}")

    # Export full download CSV files (same as chart for this dataset)
    en_full_path = datasets_dir / "imported-vehicles-total-all-en.csv"
    mn_full_path = datasets_dir / "imported-vehicles-total-all-mn.csv"

    en_total.to_csv(en_full_path, index=False)
    mn_total.to_csv(mn_full_path, index=False)
    print(f"\nDownload CSV files created:")
    print(f"  {en_full_path}")
    print(f"  {mn_full_path}")

    # Export XLSX (wide format - just one column of values in this case)
    xlsx_path = datasets_dir / "imported-vehicles-total.xlsx"

    # For this simple time series, wide format is just year + value
    with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
        # English sheet
        en_excel = en_total.copy()
        en_excel.columns = ['Year', 'Total Vehicles Imported']
        en_excel.to_excel(writer, sheet_name='Data (English)', index=False)

        # Mongolian sheet
        mn_excel = mn_total.copy()
        mn_excel.columns = ['Он', 'Нийт импортолсон тээврийн хэрэгсэл']
        mn_excel.to_excel(writer, sheet_name='Data (Mongolian)', index=False)

        # Auto-adjust column widths
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for idx, col in enumerate(worksheet.iter_cols()):
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 40)
                worksheet.column_dimensions[column].width = adjusted_width

    print(f"\nXLSX file created: {xlsx_path}")

    # Print sample data
    print("\nSample data (first 5 rows):")
    print(en_total.head())

    return {
        'row_count': len(en_total),
        'first_year': int(en_total['year'].min()),
        'last_year': int(en_total['year'].max()),
        'min_value': float(en_total['value'].min()),
        'max_value': float(en_total['value'].max())
    }

if __name__ == '__main__':
    stats = main()
    print(f"\nDataset statistics: {stats}")
