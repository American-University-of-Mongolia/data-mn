# Data.mn Intern Tasks — Week of Mar 2, 2026

## Overview

**Primary goals this week:**

1. Complete carryover tasks from last week.
2. Add first-class MongolBank source support (skill + production datasets).
3. Eliminate repeat PR quality issues (EN/MN numeric mismatch, XLSX format issues, stale branches).

**Expected output this week:** 6 merged dataset PRs + 1 merged skill PR.

---

## Dlgvn

### 1. Poverty rate (carryover)

- **Source:** NSO 1212.mn
- **Task:** Add national poverty rate with urban/rural split if available
- **Branch:** `add/poverty-rate`
- **Expected datasets:** `poverty-rate-national`, `poverty-rate-urban-rural` (if source supports split)

### 2. MongolBank source skill (new)

- **Task:** Create dedicated skill for Bank of Mongolia workflows
- **Branch:** `feat/skill-mongolbank-source`
- **Required files:**
  - `.claude/skills/datamn-source-mongolbank/SKILL.md`
  - `.claude/skills/datamn-source-mongolbank/fetch_exchange_rates.py`
  - `.claude/skills/datamn-source-mongolbank/fetch_bulletin_table.py` (or equivalent helper)
- **Skill must include:**
  - source navigation + update detection
  - bilingual vs single-language translation flow
  - CSV output contract for data.mn ingestion
  - examples for exchange rates + one monthly indicator

### 3. Official daily exchange rate dataset

- **Source:** MongolBank official daily rate page
- **Branch:** `add/mongolbank-exchange-rates-daily`
- **Expected dataset ID:** `mongolbank-exchange-rates-daily`
- **Expected coverage:** daily rates for major currencies (USD, EUR, CNY, RUB, JPY, KRW)

### 4. MongolBank policy rate dataset

- **Source:** MongolBank statistics/bulletins
- **Branch:** `add/mongolbank-policy-rate`
- **Expected dataset ID:** `mongolbank-policy-rate`
- **Expected coverage:** policy rate history over time (monthly or event-based with date series)

---

## OkuOrgil3757

### 1. Teachers by education level (carryover)

- **Source:** NSO 1212.mn
- **Task:** Add number of teachers by level (primary, secondary, higher ed)
- **Branch:** `add/teachers-by-level`
- **Expected dataset ID:** `teachers-by-level`

### 2. Average wages by sector (carryover)

- **Source:** NSO 1212.mn
- **Task:** Add/update wage-by-sector dataset without duplicating existing salary datasets
- **Branch:** `add/average-wages`
- **Expected output:** clear coverage note in PR explaining how this differs from existing salary datasets

### 3. MongolBank money supply (M2) dataset

- **Source:** MongolBank monthly statistics
- **Branch:** `add/mongolbank-money-supply-m2`
- **Expected dataset ID:** `mongolbank-money-supply-m2`
- **Expected coverage:** monthly M2 trend

### 4. MongolBank lending/deposit reference rate dataset

- **Source:** MongolBank statistics
- **Branch:** `add/mongolbank-reference-rates`
- **Expected dataset ID:** `mongolbank-reference-rates`
- **Expected coverage:** key reference rates by date (clear metadata for each rate type)

---

## Workflow Requirements (Mandatory)

For each task PR:

1. Sync branch from latest main before opening PR:
   ```bash
   gh repo sync
   git checkout main
   git pull
   git checkout -b <branch-name>
   ```
2. Use `/data-add` workflow and required skills.
3. One dataset per PR (except the skill PR, which must be skill-only).
4. Rebase from `main` before final push to reduce merge conflicts.

---

## Validation Gate (Mandatory Before PR)

Run for each dataset ID:

```bash
conda run -n datamn python tools/tests/run_all_checks.py <dataset-id>
python3 tools/scripts/validate_dataset.py --all <dataset-id> --base-dir data.mn
python3 tools/scripts/validate_vega.py data.mn/public/charts/<dataset-id>-en.json
python3 tools/scripts/validate_vega.py data.mn/public/charts/<dataset-id>-mn.json
python3 tools/scripts/validate_mdx_datafiles.py
cd data.mn && npm run build && npm run check
```

**Hard fail conditions (do not open PR):**

- EN/MN numeric mismatch (`4.14`, `8.7`)
- XLSX not wide-form (`5.5`)
- Missing generic XLSX (`1.5`)
- Missing EN/MN MDX or chart files

---

## PR Checklist

Before requesting review, confirm:

- [ ] EN and MN CSV files created
- [ ] Generic XLSX file created (`<dataset-id>.xlsx`)
- [ ] EN and MN chart JSON files created
- [ ] EN and MN MDX pages created
- [ ] Registry entry added/updated correctly
- [ ] `run_all_checks.py` passes for dataset(s)
- [ ] `validate_mdx_datafiles.py` passes
- [ ] `npm run build` succeeds
- [ ] PR includes short coverage note and source URL

---

## Review/Merge Order

1. Skill PR (`feat/skill-mongolbank-source`)
2. Carryover NSO tasks (`poverty-rate`, `teachers-by-level`, `average-wages`)
3. MongolBank dataset PRs

This order reduces rework and ensures MongolBank datasets follow the finalized source skill.
