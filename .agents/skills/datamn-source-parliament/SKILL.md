---
name: datamn-source-parliament
description: Pull, normalize, register, publish, and validate data.mn datasets for Mongolian Parliament plenary attendance, MP arrival times, sitting start times, and the parliament.mn attendance archive. Use for Parliament attendance or punctuality data work in the data.mn repository.
---

# Data.mn Parliament Source

Use `https://att.parliament.mn/` as the structured source for the current
Parliament and `https://www.parliament.mn/nc/635/` as the publication archive
and historical-backfill source. No authentication is required.

## Pull and Build

Run from the repository root:

```bash
uv run python .agents/skills/datamn-source-parliament/scripts/fetch_data.py
uv run python tools/sources/parliament/register.py
uv run python tools/sources/parliament/build_public.py
uv run python tools/scripts/rebuild_downloads.py --dataset mp-parliament-attendance --apply
uv run python tools/scripts/rebuild_downloads.py --dataset parliament-session-attendance --apply
```

The wrapper calls the established collector in `.claude/skills` so Codex and
Claude use one implementation. Normalized source files are written under
`tools/sources/parliament/raw/`.

Register the source and unpublished parent before building child datasets.
The build deliberately fails if either is missing. Never publish the parent
`parliament-attendance-records`; publish only the two public child datasets.

## Source Invariants

- Preserve all seven official statuses: present, late, general leave, medical
  leave, domestic assignment, foreign assignment, and unexplained absence.
- Never collapse approved leave or official assignment into unexplained absence.
- Keep official punctuality relative to the actual-start threshold distinct
  from arrival relative to the publicly scheduled start.
- Leave timing fields blank when Parliament did not publish the required time;
  never impute a default sitting time.
- Re-pull the full current-term snapshot because Parliament can revise earlier
  attendance statuses. Do not use a new-dates-only update.
- Fail closed on unknown statuses, conflicting sitting dates, an incomplete MP
  by sitting matrix, or an inconsistent archive count.
- Do not create a composite MP ranking.

## Validation and Publication

After every build, run:

```bash
.venv/bin/python tools/scripts/validate_dataset.py --all mp-parliament-attendance --base-dir data.mn
.venv/bin/python tools/scripts/validate_dataset.py --all parliament-session-attendance --base-dir data.mn
cd data.mn && python3 ../tools/scripts/validate_vega.py --all --quiet
```

Publishing assigns permanent URLs and is an explicit registry mutation. Once
authorized, publish the stable dataset IDs as their canonical slugs:

```bash
cd tools
python3 -m registry publish mp-parliament-attendance
python3 -m registry publish parliament-session-attendance
```

Do not deploy merely because registry publication was authorized.

## Historical Backfill

Treat the mixed-format archive as a separate phase. Retain each article and
attachment URL, reconcile duplicate daily/monthly summaries, and record the
status mapping before merging historical rows into the normalized dataset.

For field definitions, output paths, and provenance details, read
`tools/sources/parliament/source.md` and the dataset definitions in
`tools/sources/parliament/datasets/`.
