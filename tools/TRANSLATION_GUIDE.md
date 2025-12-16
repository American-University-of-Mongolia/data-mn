# Translation Guide for Single-Language Data Sources

## Overview

The data.mn platform uses a **bilingual architecture** where:
- All datasets MUST have both English (`-en.csv`) and Mongolian (`-mn.csv`) versions
- Charts reference language-specific CSVs (EN charts use `-en.csv`, MN charts use `-mn.csv`)
- MDX pages are generated in both languages with appropriate data files

While NSO 1212.mn provides data in both languages via API, many other sources only provide data in ONE language. This guide explains how to handle these single-language sources.

## When Translation Is Needed

| Source Type | Language | Translation Required |
|------------|----------|---------------------|
| NSO 1212.mn API | EN + MN | No - fetch both |
| MRPAM PDFs | MN only | Yes - translate to EN |
| MongolBank PDFs | MN only | Yes - translate to EN |
| MongolBank web pages | Mixed | Depends on dataset |
| International sources | EN only | Yes - translate to MN |
| Government PDFs | Usually MN | Yes - translate to EN |

## Translation Strategy

### What Gets Translated

#### 1. Column Names (Always)
```python
# Mongolian → English
огноо → date
салбар → sector
утга → value

# English → Mongolian
year → он
region → бүс
amount → дүн
```

#### 2. Categorical/String Values
```python
# Gender
Эрэгтэй → Male
Эмэгтэй → Female

# Location
Улаанбаатар → Ulaanbaatar
Хот → Urban
Хөдөө → Rural

# Sectors
Уул уурхай → Mining
Боловсрол → Education
```

#### 3. What NOT to Translate
- Numeric values (same in both languages)
- ISO codes (MN, USD, EUR)
- Date values in ISO format (2024-01-01)
- Identifiers and codes

### Translation Workflow

#### Step 1: Extract/Fetch Source Data
```python
# Example: Extract from MRPAM PDF (Mongolian)
import pdfplumber
import pandas as pd

with pdfplumber.open('2025.10.stat.report.mon.pdf') as pdf:
    table = pdf.pages[2].extract_table()
    df_mn = pd.DataFrame(table[1:], columns=table[0])
    df_mn.to_csv('mrpam-coal-raw-mn.csv', index=False)
```

#### Step 2: Identify Translation Needs
```python
# Analyze the DataFrame
df = pd.read_csv('mrpam-coal-raw-mn.csv')

# Find categorical columns (non-numeric)
string_cols = df.select_dtypes(include=['object']).columns
print(f"String columns: {list(string_cols)}")

# Check unique values in each string column
for col in string_cols:
    unique_vals = df[col].unique()
    print(f"{col}: {unique_vals}")
```

#### Step 3: Use Translation Script
```bash
# Auto-detect language and translate
python3 tools/scripts/translate_csv.py input.csv --auto -o output.csv

# Or specify direction explicitly
python3 tools/scripts/translate_csv.py mrpam-coal-mn.csv --from mn --to en -o mrpam-coal-en.csv
```

#### Step 4: Validate Output
```python
# Check both files
df_mn = pd.read_csv('dataset-mn.csv')
df_en = pd.read_csv('dataset-en.csv')

print(f"MN: {len(df_mn)} rows, {len(df_mn.columns)} columns")
print(f"EN: {len(df_en)} rows, {len(df_en.columns)} columns")

# Verify numeric columns match
numeric_cols_mn = df_mn.select_dtypes(include=['number'])
numeric_cols_en = df_en.select_dtypes(include=['number'])

assert numeric_cols_mn.shape == numeric_cols_en.shape, "Numeric column count mismatch!"
assert numeric_cols_mn.equals(numeric_cols_en), "Numeric values differ!"

print("✓ Validation passed")
```

## Standard Translation Mappings

### Column Names

#### Time-Related
```python
{
    'он': 'year',
    'сар': 'month',
    'улирал': 'quarter',
    'огноо': 'date',
    'хугацаа': 'period',
}
```

#### Geography
```python
{
    'аймаг': 'province',
    'дүүрэг': 'district',
    'сум': 'soum',
    'хороо': 'khoroo',
    'бүс': 'region',
    'хот': 'city',
    'газар_нутаг': 'location',
}
```

#### Demographics
```python
{
    'хүйс': 'sex',
    'нас': 'age',
    'насны_бүлэг': 'age_group',
    'хүн_ам': 'population',
}
```

#### Economics
```python
{
    'салбар': 'sector',
    'үнэ': 'price',
    'утга': 'value',
    'дүн': 'amount',
    'хувь': 'percentage',
    'өсөлт': 'growth',
    'орлого': 'income',
    'зардал': 'expenditure',
}
```

### Common Values

#### Gender
```python
{
    'Эрэгтэй': 'Male',
    'Эмэгтэй': 'Female',
    'Нийт': 'Total',
}
```

#### Urban/Rural
```python
{
    'Хот': 'Urban',
    'Хөдөө': 'Rural',
}
```

#### Ulaanbaatar Districts
```python
{
    'Улаанбаатар': 'Ulaanbaatar',
    'Хан-Уул': 'Khan-Uul',
    'Баянзүрх': 'Bayanzurkh',
    'Сүхбаатар': 'Sukhbaatar',
    'Чингэлтэй': 'Chingeltei',
    'Баянгол': 'Bayangol',
    'Сонгинохайрхан': 'Songinokhairkhan',
    'Налайх': 'Nalaikh',
    'Багануур': 'Baganuur',
}
```

#### Economic Sectors
```python
{
    'Уул уурхай': 'Mining',
    'Боловсрол': 'Education',
    'Эрүүл мэнд': 'Health',
    'Барилга': 'Construction',
    'Үйлдвэрлэл': 'Manufacturing',
    'Худалдаа': 'Trade',
    'Тээвэр': 'Transportation',
    'Санхүү': 'Finance',
    'Хөдөө аж ахуй': 'Agriculture',
}
```

## Manual Translation Workflow

If `translate_csv.py` doesn't have the needed translations, translate manually:

### Example: Mongolian to English

```python
import pandas as pd

# Load Mongolian data
df_mn = pd.read_csv('source-mn.csv')

# Define custom translations
column_map = {
    'огноо': 'date',
    'олборлолт_мян_тн': 'production_kt',
    'экспорт_мян_тн': 'export_kt',
    'дотоод_мян_тн': 'domestic_kt'
}

value_map = {
    'салбар': {  # sector column
        'Уул уурхай': 'Mining',
        'Боловсрол': 'Education',
        # ... add more as needed
    }
}

# Create English version
df_en = df_mn.copy()

# Translate column names
df_en = df_en.rename(columns=column_map)

# Translate values
for col_mn, col_en in column_map.items():
    if col_mn in value_map:
        df_en[col_en] = df_en[col_en].map(value_map[col_mn])

# Save both versions
df_mn.to_csv('dataset-id-mn.csv', index=False)
df_en.to_csv('dataset-id-en.csv', index=False)
```

### Example: English to Mongolian

```python
import pandas as pd

# Load English data
df_en = pd.read_csv('source-en.csv')

# Define reverse translations
column_map = {
    'date': 'огноо',
    'sector': 'салбар',
    'value': 'утга',
}

value_map = {
    'sector': {
        'Mining': 'Уул уурхай',
        'Education': 'Боловсрол',
        'Health': 'Эрүүл мэнд',
    },
    'region': {
        'Urban': 'Хот',
        'Rural': 'Хөдөө',
    }
}

# Create Mongolian version
df_mn = df_en.copy()

# Translate column names
df_mn = df_mn.rename(columns=column_map)

# Translate values
for col_en, col_mn in column_map.items():
    if col_en in value_map:
        df_mn[col_mn] = df_mn[col_mn].map(value_map[col_en])

# Save both versions
df_en.to_csv('dataset-id-en.csv', index=False)
df_mn.to_csv('dataset-id-mn.csv', index=False)
```

## Best Practices

### 1. Consistency
- Use the same translations across all datasets
- Check existing datasets for precedent
- Document new translations in source.md

### 2. Standard Mappings First
- Always check `tools/scripts/translate_csv.py` for existing mappings
- Add new standard mappings to the script if they're reusable
- Keep source-specific translations in source.md

### 3. Validation
- Always validate that row counts match
- Verify numeric columns are identical
- Check that no values are left untranslated
- Review sample rows manually

### 4. Documentation
- Document translation mappings in source.md
- Note any specialized terminology
- Flag items needing human review

### 5. Human Review
Recommended for:
- Medical terminology
- Legal terms
- Technical specifications
- First dataset from a new source
- Ambiguous translations

## Source-Specific Workflows

### MRPAM (Mongolian PDFs)
```bash
# 1. Extract from PDF using datamn-extract-pdf skill
python3 extract_mrpam.py

# 2. Translate
python3 tools/scripts/translate_csv.py mrpam-coal-mn.csv --from mn --to en -o mrpam-coal-en.csv

# 3. Validate
python3 tools/scripts/validate_bilingual.py mrpam-coal-mn.csv mrpam-coal-en.csv

# 4. Save to public/datasets/
cp mrpam-coal-*.csv data.mn/public/datasets/
```

### MongolBank (Mixed)
```bash
# Check if dataset is bilingual or single-language
# If bilingual: fetch both versions separately
# If single-language: follow MRPAM workflow above
```

### International Sources (English)
```bash
# 1. Fetch English data
curl https://example.com/data.csv -o dataset-en.csv

# 2. Translate to Mongolian
python3 tools/scripts/translate_csv.py dataset-en.csv --from en --to mn -o dataset-mn.csv

# 3. Manual review of Mongolian translation (recommended)
```

## Error Handling

### Untranslated Values
If translation script can't translate all values:

1. Review the output warnings
2. Add missing translations to `translate_csv.py` or use custom mapping
3. Re-run translation
4. If term is highly specialized, keep original and document

### Column Count Mismatch
If translated CSV has different column count:

1. Check for date/identifier columns that shouldn't be translated
2. Verify translation mappings don't create duplicate columns
3. Review date handling (some date columns might be split/merged)

### Numeric Data Changes
If numeric validation fails:

1. Check for number formatting issues (commas vs periods)
2. Verify no numeric columns were accidentally translated
3. Look for currency conversion issues

## Integration with data-add Command

When using `/data-add` with single-language sources:

1. System detects source language automatically
2. Asks: "This source is Mongolian-only. Translate to English?"
3. Applies translation workflow
4. Validates bilingual output
5. Proceeds with normal dataset creation

See `.claude/commands/data-add.md` section "Language and Translation Workflow" for details.

## Tools Reference

### Translation Script
```bash
# Location
tools/scripts/translate_csv.py

# Usage
python3 translate_csv.py INPUT --auto -o OUTPUT
python3 translate_csv.py INPUT --from mn --to en -o OUTPUT
python3 translate_csv.py INPUT --from en --to mn -o OUTPUT

# Features
- Auto language detection
- Standard translation mappings
- Preserves numeric data
- Validation built-in
```

### Standard Mappings
All standard translations are defined in:
- `tools/scripts/translate_csv.py` (Python dictionaries)
- `.claude/skills/datamn-source-template/SKILL.md` (Documentation)

### Source-Specific Mappings
Documented in:
- `tools/sources/mrpam/source.md`
- `tools/sources/mongolbank/source.md`
- `tools/sources/{source-id}/source.md`

## Examples

### Complete Example: MRPAM Coal Production

**Source**: MRPAM monthly report PDF (Mongolian)
**Goal**: Create bilingual CSVs for coal production data

```python
# 1. Extract from PDF (results in Mongolian data)
import pdfplumber
import pandas as pd

with pdfplumber.open('2025.10.stat.report.mon.pdf') as pdf:
    # Extract coal production table from page 3
    table = pdf.pages[2].extract_table()

# 2. Create DataFrame
headers = ['огноо', 'олборлолт_мян_тн', 'экспорт_мян_тн', 'дотоод_мян_тн']
df_mn = pd.DataFrame(table[1:], columns=headers)

# 3. Save Mongolian version
df_mn.to_csv('mrpam-coal-production-mn.csv', index=False)

# 4. Translate to English using script
# python3 tools/scripts/translate_csv.py mrpam-coal-production-mn.csv --from mn --to en -o mrpam-coal-production-en.csv

# Result:
# mrpam-coal-production-mn.csv: огноо, олборлолт_мян_тн, экспорт_мян_тн, дотоод_мян_тн
# mrpam-coal-production-en.csv: date, production_kt, export_kt, domestic_kt
```

### Complete Example: International Data to Mongolian

**Source**: World Bank API (English)
**Goal**: Create bilingual CSVs for GDP data

```python
# 1. Fetch English data
import pandas as pd

df_en = pd.read_csv('worldbank-gdp-en.csv')
# Columns: year, country, sector, gdp_usd

# 2. Translate to Mongolian
# python3 tools/scripts/translate_csv.py worldbank-gdp-en.csv --from en --to mn -o worldbank-gdp-mn.csv

# 3. Result
# worldbank-gdp-en.csv: year, country, sector, gdp_usd
# worldbank-gdp-mn.csv: он, улс, салбар, ДНБ_доллар

# 4. Manual review recommended for country names
```

## Checklist

When adding a single-language dataset:

- [ ] Identified source language (EN or MN)
- [ ] Extracted/fetched source data
- [ ] Created first language CSV with `-lang` suffix
- [ ] Ran translation script to create second language CSV
- [ ] Validated both CSVs have matching structure
- [ ] Verified numeric columns are identical
- [ ] Checked for untranslated categorical values
- [ ] Documented any custom translations in source.md
- [ ] Saved both CSVs to `public/datasets/`
- [ ] Generated bilingual MDX pages referencing correct CSVs
- [ ] Created Vega charts using appropriate language CSV

## Future Improvements

Potential enhancements to the translation workflow:

1. **Translation Memory**: Cache translations across datasets
2. **Specialized Dictionaries**: Medical, legal, technical term databases
3. **Validation Tool**: Dedicated script for bilingual CSV validation
4. **Translation API**: Google Translate fallback for unknown terms
5. **Review Interface**: UI for reviewing and approving translations
6. **Consistency Checker**: Ensure same terms translated consistently across datasets

---

For more information, see:
- `.claude/skills/datamn-source-template/SKILL.md` - Source template with translation section
- `.claude/commands/data-add.md` - Dataset addition workflow
- `tools/scripts/translate_csv.py` - Translation script
- `tools/sources/{source}/source.md` - Source-specific documentation
