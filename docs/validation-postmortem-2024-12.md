# Validation Postmortem: Data-Add Agent Failures (December 2024)

## Summary

On 2024-12-06, the `/data-batch` command was used to create 7 new datasets for the data.mn home page cards. Three charts failed to render correctly despite passing validation. This document analyzes the root causes and documents the fixes implemented.

## Issues Identified

### Issue 1: CSV Whitespace in Category Values

**Symptom:** `unemployment-by-sex` chart showed blank - no data visible despite CSV having correct data.

**Root Cause:** The CSV file had leading whitespace in the Category column:
```csv
Category,Year,value
        Female,2009,11.6
        Male,2009,11.6
```

When Vega-Lite tried to match the color domain `["Male", "Female"]` against the CSV values `["        Male", "        Female"]`, no match occurred, so no colors were assigned.

**Why Validation Didn't Catch It:**
- `validate_csv()` checked for column naming issues but NOT for whitespace in values
- `validate_vega.py` validated chart structure but didn't cross-reference with actual data

**Fix Applied:** Added whitespace detection to `validate_dataset.py`:
```python
# Check for leading whitespace
leading_ws = df[col].astype(str).str.match(r'^\s+')
if leading_ws.any():
    result.add_error(f"Column '{col}' has values with LEADING WHITESPACE...")
```

---

### Issue 2: Chart File Naming Without Language Suffix

**Symptom:** `trade-total` and `trade-exports-imports` charts showed "Chart not found" errors.

**Root Cause:** Workers created chart files as:
- `trade-total.json` (no language suffix)
- `trade-exports-imports.json` (no language suffix)

But MDX pages referenced:
- `/charts/trade-total-en.json`
- `/charts/trade-exports-imports-mn.json`

**Why Validation Didn't Catch It:**
- `validate_chart()` only validated JSON structure, not file naming
- `validate_mdx()` checked if referenced files exist but the unreferenced files weren't validated together

**Fix Applied:** Added naming convention checks to `validate_chart()`:
```python
filename = os.path.basename(file_path)
if not (filename.endswith('-en.json') or filename.endswith('-mn.json')):
    result.add_warning("Chart file should have language suffix...")
```

---

### Issue 3: Extra Files Without Language Suffix

**Symptom:** 52 CSV files existed instead of expected ~46.

**Root Cause:** Workers created intermediate/base files:
- `labor-participation-national.csv` (should only have `-en.csv` and `-mn.csv`)
- `salary-average-national.csv`
- `nso-0600-013v2-en.csv` (raw fetch files, should be cleaned up)

**Why This Happened:**
- Workers saved intermediate processing steps to wrong directory
- No cleanup step after processing

**Fix Applied:** Manually deleted extra files. Consider adding validation to flag unexpected files.

---

## Validation Enhancements Made

### 1. CSV Whitespace Detection (CRITICAL)

Added to `validate_dataset.py`:
- Detects leading whitespace in string columns (ERROR - blocks validation)
- Detects trailing whitespace (WARNING)
- Detects whitespace-only values (WARNING)

This would have caught Issue #1.

### 2. Chart File Naming Validation

Added to `validate_dataset.py`:
- Verifies chart files end with `-en.json` or `-mn.json`
- Warns if chart references CSV without matching language suffix

This would have caught Issue #2.

### 3. Chart-CSV Cross-Validation (NEW)

Added new function `validate_chart_csv_consistency()`:
- Extracts color domain from chart spec
- Compares against actual CSV categorical values
- Detects whitespace mismatches (ERROR)
- Detects missing domain values (WARNING)

This provides defense-in-depth for color matching issues.

---

## Why Tests Passed But Charts Failed

### The Gap Between "Structurally Valid" and "Functionally Correct"

Previous validation checked:
- ✅ JSON is valid
- ✅ Vega-Lite schema is correct
- ✅ CSV parses successfully
- ✅ MDX frontmatter is valid

But didn't check:
- ❌ CSV values match chart color domains exactly
- ❌ Files follow naming conventions
- ❌ Chart-to-data URL paths are consistent

**Lesson:** Structural validation is necessary but not sufficient. Cross-file validation and content consistency checks are required.

---

## Recommendations for Agent Instructions

### 1. Update `datamn-dataset-worker.md`

Add explicit validation step for CSV content:
```markdown
### Step 3.5: Validate CSV Content Quality

Before proceeding, check CSV for common issues:
- Strip whitespace from all string columns
- Verify column names are lowercase
- Remove any intermediate/debug rows
```

### 2. Enforce Bilingual File Naming

Add to worker instructions:
```markdown
### File Naming Requirements (STRICT)

All files MUST have language suffix:
- CSV: `{dataset-id}-en.csv` and `{dataset-id}-mn.csv`
- Charts: `{dataset-id}-en.json` and `{dataset-id}-mn.json`

DO NOT create files without language suffix (e.g., `dataset.csv`).
```

### 3. Add Cleanup Step

Add to worker instructions:
```markdown
### Step 10.5: Cleanup

Before finalizing, remove any intermediate files:
- Delete raw fetch files (e.g., `nso-*.csv`)
- Delete non-suffixed base files
- Verify only `-en` and `-mn` files remain
```

---

## Test Commands for Verification

Run these to verify validation catches issues:

```bash
# Test whitespace detection
cd data && python3 tools/scripts/validate_dataset.py --csv /tmp/whitespace-test.csv

# Test full dataset validation
cd data && python3 tools/scripts/validate_dataset.py --all unemployment-by-sex --base-dir data.mn

# Test chart naming
cd data && python3 tools/scripts/validate_dataset.py --chart data.mn/public/charts/trade-total-en.json
```

---

## Checklist for Future Dataset Creation

Before marking a dataset complete, verify:

- [ ] All CSV files have `-en` and `-mn` suffixes
- [ ] All chart files have `-en` and `-mn` suffixes
- [ ] No intermediate/raw files left in `public/datasets/`
- [ ] `validate_dataset.py --all {dataset-id}` passes with no errors
- [ ] Visual QA: charts render correctly on localhost:4321

---

## Files Modified

1. `tools/scripts/validate_dataset.py`
   - Added whitespace detection in `validate_csv()`
   - Added file naming checks in `validate_chart()`
   - Added new `validate_chart_csv_consistency()` function
   - Enhanced `validate_all()` to include cross-validation

2. This postmortem document: `docs/validation-postmortem-2024-12.md`
