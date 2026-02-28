---
name: datamn-worker-discovery
description: "Discover data sources and table structures before dataset creation. Use when searching source systems, checking freshness, or recommending split definitions for data.mn datasets."
---


# Discovery Worker

Use this skill when a request needs discovery only (no file creation).

## Required Outputs

Return structured findings including:

- source and table identifiers
- dimension/value structure
- update timestamp/freshness
- recommended split candidates with filter criteria

## Core Steps

1. Read source definition from `tools/sources/<source-id>/source.md`.
2. For NSO discovery, use `data/.claude/skills/datamn-source-nso/query_api.py`.
3. For web/PDF sources, gather metadata and latest publication indicators.
4. Propose split-friendly dataset shapes (Statista-style narrow pages).
5. Stop before creating files.

## Validation

- Ensure recommendations are feasible with available dimensions.
- Call out ambiguity explicitly (missing dimensions, unstable codes, sparse ranges).
