# /data-validate - Validate All Datasets

Run comprehensive validation across all data.mn datasets and generate a report.

## Usage

```
/data-validate              # Validate all datasets
/data-validate gdp-nominal  # Validate single dataset
/data-validate --fix        # Validate and fix issues automatically
```

## What This Command Does

1. **Dynamically discover all datasets** from `src/data/data/en/*.mdx` (no hardcoded list)
2. **Run validation scripts** on each dataset
3. **Compile results** into a prioritized report
4. **Optionally fix** issues automatically

## Execution Steps

### Step 1: Get Dataset List

```bash
cd /home/ritz/Insync/robert@aum.edu.mn/Google\ Drive/data/data.mn
ls src/data/data/en/*.mdx | xargs -n1 basename | sed 's/.mdx//'
```

### Step 2: Run Validation on Each Dataset

For each dataset ID, run:

```bash
python ../tools/scripts/validate_dataset.py --all {id} --base-dir .
```

Capture the output and parse for:
- ✅ VALID entries
- ❌ INVALID entries (ERRORS)
- ⚠️ WARNING entries

### Step 3: Run Chart Validation

```bash
python ../tools/scripts/validate_vega.py --all
```

### Step 4: Generate Report

Compile findings into this format:

```markdown
# Data.mn Validation Report

**Date**: {date}
**Datasets Scanned**: {count}
**Charts Scanned**: {count}

## Summary

| Status | Count |
|--------|-------|
| ✅ Passed | X |
| ❌ Failed | X |
| ⚠️ Warnings | X |

## Critical Issues (Chart Failures)

These cause charts to render incorrectly or show no data:

1. **{dataset}**: {issue description}
   - File: `{path}`
   - Fix: {specific fix instruction}

## Required Fixes (Validation Errors)

These must be fixed for data quality:

1. **{dataset}**: {issue description}
   - File: `{path}`
   - Fix: {specific fix instruction}

## Warnings (Recommendations)

These are suggestions for improvement:

1. **{dataset}**: {issue description}

## Datasets Passing All Checks

- dataset-1 ✅
- dataset-2 ✅
- ...
```

## Issue Priority

### Critical (fix immediately)
- Chart-CSV language mismatch (7.1-7.4)
- CSV whitespace issues (4.7-4.9)
- Chart data URL wrong language (6.7-6.8)

### Required (fix before deploy)
- Missing files (1.1-1.7)
- Invalid frontmatter fields (2.x)
- Hover pattern issues (6.11-6.18)
- MN CSV with English headers (4.10-4.11)

### Warnings (fix when convenient)
- Aliased categories (use canonical)
- Missing definition files
- Missing version backups
- Tooltip type hints

## Auto-Fix Mode (--fix)

When `--fix` flag is provided, automatically fix these issues:

1. **CSV whitespace**: Strip leading/trailing whitespace from all values
2. **Aliased categories**: Update to canonical category names
3. **Missing tooltip types**: Add type annotations

Do NOT auto-fix:
- Missing files (need human decision on content)
- Chart-CSV language mismatch (needs careful review)
- Content quality issues

## Example Output

```
$ /data-validate

Scanning 41 datasets...

[1/41] bop-current-account... ✅ PASS
[2/41] bop-fdi-net... ✅ PASS
[3/41] gdp-nominal... ❌ FAIL (1 error)
[4/41] labor-participation-by-sex... ⚠️ WARN (2 warnings)
...

=== VALIDATION COMPLETE ===

Summary:
- 38 datasets passed
- 2 datasets failed
- 5 datasets have warnings

Critical Issues (2):
1. gdp-nominal-mn.csv: English headers in MN file
2. labor-participation-by-sex-mn.csv: English headers in MN file

See full report above.

Would you like me to fix the auto-fixable issues? (y/n)
```

## Checklist Reference

Full checklist at: `tools/config/data-page-checklist.md`

85 checks across 10 sections:
1. File Existence (7)
2. MDX Frontmatter (25)
3. MDX Body (5)
4. CSV Data (14)
5. XLSX File (6)
6. Chart Specs (21)
7. Chart-CSV Consistency (4)
8. Bilingual Consistency (7)
9. Registry Sync (6)
10. Content Quality (6)
