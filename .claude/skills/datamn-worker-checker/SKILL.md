---
name: datamn-worker-checker
description: "Independently validate dataset outputs after dataset worker execution, covering CSV/XLSX/chart/MDX/regsitry consistency and cross-language integrity checks."
---


# Checker Worker

Use this skill as an independent pass after dataset generation.

## Core Checks

- dataset-level validation (`validate_dataset.py --all`)
- chart validation for EN/MN JSON specs
- MDX dataFiles correctness and component usage
- EN/MN row and numeric consistency
- registry entry correctness and status

## Commands

```bash
tools/scripts/codex_data_runner.sh validate <dataset_id>
tools/scripts/codex_data_runner.sh validate-charts
tools/scripts/codex_data_runner.sh validate-mdx
```

## Output Contract

Return pass/fail with explicit blocking errors and non-blocking warnings.
