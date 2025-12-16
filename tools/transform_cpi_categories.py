#!/usr/bin/env python3
"""
Transform CPI data to create category comparison dataset
"""
import pandas as pd
from openpyxl.utils import get_column_letter

# Paths
base_dir = "/home/ritz/Insync/robert@aum.edu.mn/Google Drive/data"
input_en = f"{base_dir}/tools/versions/nso-cpi-ulaanbaatar-mom/nso-0600-003v4-en.csv"
input_mn = f"{base_dir}/tools/versions/nso-cpi-ulaanbaatar-mom/nso-0600-003v4-mn.csv"
output_dir = f"{base_dir}/data.mn/public/datasets"

# Load data
df_en = pd.read_csv(input_en)
df_mn = pd.read_csv(input_mn)

# Filter for reference year 2023=100 and latest month (2025-11)
# EN columns: Reference year, Group, Month, value
# MN columns: Суурь он, Бүлэг, Сар, value
df_en = df_en[(df_en['Reference year'] == '2023=100') & (df_en['Month'] == '2025-11')].copy()
df_mn = df_mn[(df_mn['Суурь он'] == '2023=100') & (df_mn['Сар'] == '2025-11')].copy()

# Exclude "Overall index" / "Ерөнхий индекс"
df_en = df_en[df_en['Group'] != 'Overall index'].copy()
df_mn = df_mn[df_mn['Бүлэг'] != 'Ерөнхий индекс'].copy()

# Strip whitespace from Group column (CRITICAL for chart color matching)
df_en['Group'] = df_en['Group'].str.strip()
df_mn['Бүлэг'] = df_mn['Бүлэг'].str.strip()

# Convert value to numeric
df_en['value'] = pd.to_numeric(df_en['value'], errors='coerce')
df_mn['value'] = pd.to_numeric(df_mn['value'], errors='coerce')

# Rename columns to final format
df_en = df_en[['Group', 'value']].rename(columns={'Group': 'category'})
df_mn = df_mn[['Бүлэг', 'value']].rename(columns={'Бүлэг': 'category'})

# Sort by value descending
df_en = df_en.sort_values('value', ascending=False).reset_index(drop=True)
df_mn = df_mn.sort_values('value', ascending=False).reset_index(drop=True)

# Calculate statistics for excerpt
highest_cat_en = df_en.iloc[0]['category']
highest_val = df_en.iloc[0]['value']
lowest_cat_en = df_en.iloc[-1]['category']
lowest_val = df_en.iloc[-1]['value']

print("\n=== STATISTICS ===")
print(f"Month: November 2025")
print(f"Highest: {highest_cat_en} at {highest_val}%")
print(f"Lowest: {lowest_cat_en} at {lowest_val}%")
print(f"Total categories: {len(df_en)}")

# Export chart CSVs
df_en.to_csv(f"{output_dir}/cpi-by-category-ulaanbaatar-en.csv", index=False)
df_mn.to_csv(f"{output_dir}/cpi-by-category-ulaanbaatar-mn.csv", index=False)
print(f"\n✓ Chart CSVs exported to {output_dir}")

# Export XLSX (wide format - single row with categories as columns)
# For this dataset, keep it simple: category names as column headers
wide_df = pd.DataFrame([df_en.set_index('category')['value']]).T.reset_index()
wide_df.columns = ['Category', 'Change (%)']

xlsx_path = f"{output_dir}/cpi-by-category-ulaanbaatar.xlsx"
with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
    wide_df.to_excel(writer, index=False, sheet_name='November 2025')

    # Auto-adjust column widths
    worksheet = writer.sheets['November 2025']
    for idx, col in enumerate(wide_df.columns):
        max_length = max(
            wide_df[col].astype(str).map(len).max(),
            len(str(col))
        ) + 2
        col_letter = get_column_letter(idx + 1)
        worksheet.column_dimensions[col_letter].width = min(max_length, 40)

print(f"✓ XLSX exported to {xlsx_path}")

print("\n=== EXCERPT SUGGESTION ===")
print(f"In November 2025, {highest_cat_en} saw the largest price increase at {highest_val}%, while {lowest_cat_en} had the smallest change at {lowest_val}%.")
