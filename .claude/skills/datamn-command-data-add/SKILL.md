---
name: datamn-command-data-add
description: "Orchestrate the data-add workflow: source discovery, split planning, per-dataset creation, and independent checker validation for new data.mn datasets."
---


# Data Add Workflow

## Orchestration Pattern

1. Discovery phase via `datamn-worker-discovery`.
2. Confirm split plan and dataset IDs.
3. Run one `datamn-worker-dataset` per dataset (parent + splits).
4. Run `datamn-worker-checker` on each output set.
5. Iterate fixes until checker pass.

## Notes

- Keep registry metadata and URL stability rules aligned.
- Prefer small parallel batches instead of unbounded fan-out.
