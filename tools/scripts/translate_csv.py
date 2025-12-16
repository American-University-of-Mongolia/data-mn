#!/usr/bin/env python3
"""
Translate CSV data between English and Mongolian for data.mn bilingual architecture.

This script handles single-language data sources by creating the missing language version.
It translates both column names and categorical values while preserving numeric data.

Usage:
    python3 translate_csv.py input.csv --from mn --to en -o output.csv
    python3 translate_csv.py input.csv --auto  # Auto-detect language and translate
"""

import pandas as pd
import argparse
import sys
from pathlib import Path

# Standard column name translations (Mongolian → English)
COLUMN_TRANSLATIONS_MN_TO_EN = {
    # Time
    'он': 'year',
    'сар': 'month',
    'улирал': 'quarter',
    'огноо': 'date',
    'хугацаа': 'period',

    # Geography
    'аймаг': 'province',
    'дүүрэг': 'district',
    'сум': 'soum',
    'хороо': 'khoroo',
    'бүс': 'region',
    'хот': 'city',
    'нийслэл': 'capital',
    'газар_нутаг': 'location',

    # Demographics
    'хүйс': 'sex',
    'нас': 'age',
    'насны_бүлэг': 'age_group',
    'хүн_ам': 'population',

    # Economics
    'салбар': 'sector',
    'үнэ': 'price',
    'утга': 'value',
    'дүн': 'amount',
    'тоо': 'count',
    'хэмжээ': 'quantity',
    'хувь': 'percentage',
    'өсөлт': 'growth',
    'хөрөнгө_оруулалт': 'investment',
    'орлого': 'income',
    'зардал': 'expenditure',
    'ашиг': 'profit',
    'алдагдал': 'loss',

    # Units
    'нэгж': 'unit',
    'хэмжих_нэгж': 'measurement_unit',
}

# Standard value translations (Mongolian → English)
VALUE_TRANSLATIONS_MN_TO_EN = {
    # Gender
    'Эрэгтэй': 'Male',
    'Эмэгтэй': 'Female',
    'Нийт': 'Total',

    # Urban/Rural
    'Хот': 'Urban',
    'Хөдөө': 'Rural',
    'Хөдөө орон нутаг': 'Rural area',

    # Administrative divisions - Ulaanbaatar districts
    'Улаанбаатар': 'Ulaanbaatar',
    'Хан-Уул': 'Khan-Uul',
    'Баянзүрх': 'Bayanzurkh',
    'Сүхбаатар': 'Sukhbaatar',
    'Чингэлтэй': 'Chingeltei',
    'Баянгол': 'Bayangol',
    'Сонгинохайрхан': 'Songinokhairkhan',
    'Налайх': 'Nalaikh',
    'Багахангай': 'Bagakhangai',
    'Багануур': 'Baganuur',

    # Economic Sectors (ISIC-based)
    'Уул уурхай': 'Mining',
    'Боловсрол': 'Education',
    'Эрүүл мэнд': 'Health',
    'Барилга': 'Construction',
    'Үйлдвэрлэл': 'Manufacturing',
    'Худалдаа': 'Trade',
    'Тээвэр': 'Transportation',
    'Холбоо': 'Communication',
    'Санхүү': 'Finance',
    'Даатгал': 'Insurance',
    'Хөдөө аж ахуй': 'Agriculture',
    'Ойн аж ахуй': 'Forestry',
    'Загас агнуур': 'Fishing',
    'Үйлчилгээ': 'Services',
    'Зочид буудал': 'Hotels',
    'Ресторан': 'Restaurants',

    # Common categories
    'Бусад': 'Other',
    'Тодорхойгүй': 'Unspecified',
    'Үгүй': 'No',
    'Тийм': 'Yes',
}

# Reverse mappings (English → Mongolian)
COLUMN_TRANSLATIONS_EN_TO_MN = {v: k for k, v in COLUMN_TRANSLATIONS_MN_TO_EN.items()}
VALUE_TRANSLATIONS_EN_TO_MN = {v: k for k, v in VALUE_TRANSLATIONS_MN_TO_EN.items()}


def detect_language(df):
    """
    Detect if DataFrame columns are in Mongolian or English.

    Returns:
        str: 'mn' for Mongolian, 'en' for English, 'unknown' if can't determine
    """
    # Check if any column names are in Cyrillic
    cyrillic_count = sum(1 for col in df.columns if any(ord(c) >= 0x0400 and ord(c) <= 0x04FF for c in str(col)))

    if cyrillic_count > 0:
        return 'mn'

    # Check against known English columns
    english_matches = sum(1 for col in df.columns if col.lower() in COLUMN_TRANSLATIONS_EN_TO_MN)
    if english_matches > 0:
        return 'en'

    return 'unknown'


def translate_column_names(df, from_lang, to_lang):
    """Translate DataFrame column names."""
    if from_lang == 'mn' and to_lang == 'en':
        mapping = COLUMN_TRANSLATIONS_MN_TO_EN
    elif from_lang == 'en' and to_lang == 'mn':
        mapping = COLUMN_TRANSLATIONS_EN_TO_MN
    else:
        return df

    # Create translation dictionary for columns
    col_mapping = {}
    for col in df.columns:
        col_lower = col.lower().replace(' ', '_')
        if col_lower in mapping:
            col_mapping[col] = mapping[col_lower]
        elif col in mapping:
            col_mapping[col] = mapping[col]

    if col_mapping:
        df = df.rename(columns=col_mapping)
        print(f"Translated {len(col_mapping)} column names")

    return df


def translate_values(df, from_lang, to_lang):
    """Translate categorical values in DataFrame."""
    if from_lang == 'mn' and to_lang == 'en':
        mapping = VALUE_TRANSLATIONS_MN_TO_EN
    elif from_lang == 'en' and to_lang == 'mn':
        mapping = VALUE_TRANSLATIONS_EN_TO_MN
    else:
        return df

    # Identify string/categorical columns (excluding dates)
    string_cols = df.select_dtypes(include=['object']).columns
    date_keywords = ['date', 'огноо', 'year', 'он', 'month', 'сар']
    categorical_cols = [
        col for col in string_cols
        if not any(kw in col.lower() for kw in date_keywords)
    ]

    translation_count = 0
    for col in categorical_cols:
        # Get unique values
        unique_vals = df[col].dropna().unique()

        # Create mapping for this column
        col_mapping = {}
        for val in unique_vals:
            if val in mapping:
                col_mapping[val] = mapping[val]
                translation_count += 1

        # Apply mapping if any translations found
        if col_mapping:
            df[col] = df[col].map(lambda x: col_mapping.get(x, x))
            print(f"  - Column '{col}': translated {len(col_mapping)} values")

    if translation_count > 0:
        print(f"Translated {translation_count} categorical values across {len(categorical_cols)} columns")
    else:
        print("No categorical values found requiring translation")

    return df


def translate_csv(input_file, output_file, from_lang=None, to_lang=None, auto=False):
    """
    Translate a CSV file from one language to another.

    Args:
        input_file: Path to input CSV
        output_file: Path to output CSV
        from_lang: Source language ('en' or 'mn')
        to_lang: Target language ('en' or 'mn')
        auto: Auto-detect language and translate to the other
    """
    # Read CSV
    print(f"Reading {input_file}...")
    df = pd.read_csv(input_file)
    print(f"  {len(df)} rows, {len(df.columns)} columns")

    # Auto-detect language if requested
    if auto:
        from_lang = detect_language(df)
        print(f"Detected language: {from_lang}")

        if from_lang == 'mn':
            to_lang = 'en'
        elif from_lang == 'en':
            to_lang = 'mn'
        else:
            print("ERROR: Could not auto-detect language")
            return False

    if not from_lang or not to_lang:
        print("ERROR: Must specify --from and --to, or use --auto")
        return False

    print(f"\nTranslating from {from_lang.upper()} to {to_lang.upper()}...")

    # Translate column names
    df_translated = translate_column_names(df.copy(), from_lang, to_lang)

    # Translate categorical values
    df_translated = translate_values(df_translated, from_lang, to_lang)

    # Validate translation
    print("\nValidation:")
    print(f"  Original rows: {len(df)}")
    print(f"  Translated rows: {len(df_translated)}")
    print(f"  Original columns: {len(df.columns)}")
    print(f"  Translated columns: {len(df_translated.columns)}")

    # Check numeric columns are unchanged
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        # Find matching numeric columns (by position since names may have changed)
        orig_numeric = df.select_dtypes(include=['number'])
        trans_numeric = df_translated.select_dtypes(include=['number'])

        if orig_numeric.shape == trans_numeric.shape:
            if orig_numeric.equals(trans_numeric):
                print(f"  ✓ Numeric data unchanged ({len(numeric_cols)} columns)")
            else:
                print("  ⚠ WARNING: Numeric data changed!")
        else:
            print("  ⚠ WARNING: Numeric column count changed!")

    # Save translated CSV
    print(f"\nSaving to {output_file}...")
    df_translated.to_csv(output_file, index=False)
    print("Done!")

    return True


def main():
    parser = argparse.ArgumentParser(
        description='Translate CSV data between English and Mongolian',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect language and translate
  python3 translate_csv.py input.csv --auto -o output.csv

  # Explicit translation direction
  python3 translate_csv.py mongolian_data.csv --from mn --to en -o english_data.csv

  # Create bilingual pair from single-language source
  python3 translate_csv.py mrpam-coal-mn.csv --from mn --to en -o mrpam-coal-en.csv
        """
    )

    parser.add_argument('input', help='Input CSV file')
    parser.add_argument('-o', '--output', required=True, help='Output CSV file')
    parser.add_argument('--from', dest='from_lang', choices=['en', 'mn'],
                        help='Source language (en or mn)')
    parser.add_argument('--to', dest='to_lang', choices=['en', 'mn'],
                        help='Target language (en or mn)')
    parser.add_argument('--auto', action='store_true',
                        help='Auto-detect language and translate to the other')

    args = parser.parse_args()

    # Validate input file exists
    if not Path(args.input).exists():
        print(f"ERROR: Input file not found: {args.input}")
        sys.exit(1)

    # Perform translation
    success = translate_csv(
        args.input,
        args.output,
        from_lang=args.from_lang,
        to_lang=args.to_lang,
        auto=args.auto
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
