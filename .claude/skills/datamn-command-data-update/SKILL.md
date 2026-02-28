---
name: datamn-command-data-update
description: "Run source freshness checks and execute parallel update workers for stale datasets, followed by full validation and summary reporting."
---


# Data Update Workflow

## Steps

1. Read registry and identify candidate datasets.
2. Check source freshness (API/web/PDF source specific).
3. Build update queue and process in controlled parallel batches.
4. Re-run checker validations for updated datasets.
5. Summarize pass/fail and required follow-up.

## Helper Commands

```bash
tools/scripts/codex_data_runner.sh status
tools/scripts/codex_data_runner.sh info <dataset_id>
```
