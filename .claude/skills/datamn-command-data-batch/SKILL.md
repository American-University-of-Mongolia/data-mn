---
name: datamn-command-data-batch
description: "Run batched dataset onboarding for multiple topic requests using parallel discovery and controlled parallel dataset creation workers."
---


# Data Batch Workflow

## Steps

1. Parse incoming topic/source hints.
2. Run discovery workers per topic.
3. Confirm selected tables and split plans.
4. Execute dataset workers in batches (recommended max 4 in parallel).
5. Run checker validation for all created datasets.

## Rule

Treat each dataset as independently valid/invalid and report granular outcomes.
