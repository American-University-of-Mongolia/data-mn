---
name: datamn-command-data-validate
description: "Run dataset and site-level validation checks for data.mn (dataset checks, chart checks, and MDX dataFiles checks)."
---


# Data Validate Workflow

## Commands

```bash
tools/scripts/codex_data_runner.sh validate <dataset_id>
tools/scripts/codex_data_runner.sh validate-charts
tools/scripts/codex_data_runner.sh validate-mdx
```

## Rule

Validation failures are blockers for deploy-related workflows.
