---
name: datamn-worker-dataset
description: "Create or update one dataset end-to-end for data.mn, including chart/data files, MDX pages, and registry updates with mandatory validation gates."
---


# Dataset Worker

Use this skill to build exactly one dataset (parent or split).

## Non-Negotiable Rules

- Produce both EN and MN artifacts when required by source strategy.
- Keep chart CSV and download CSV/XLSX purposes distinct.
- Run validation before any final status is reported.

## Core Steps

1. Load source definition and current registry entry context.
2. Fetch/load raw data and apply split filters if needed.
3. Generate chart CSV(s), download CSV(s), and XLSX.
4. Generate EN/MN chart JSON files and EN/MN MDX pages.
5. Run:
   - `tools/scripts/validate_dataset.py`
   - `tools/scripts/validate_vega.py`
   - `tools/scripts/validate_mdx_datafiles.py`
6. Update registry only after validation passes.

## Expected Result Shape

Return a summary containing files created/updated, validation status, and any follow-up required.
