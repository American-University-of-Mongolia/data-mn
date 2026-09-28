---
name: datamn-source-parliament
description: Pull and normalize Mongolian Parliament plenary attendance, arrival times, sitting start times, MP metadata, and the parliament.mn attendance-publication archive. Use when adding, refreshing, checking, or interpreting data.mn Parliament attendance and punctuality datasets.
---

# Parliament Attendance Source

Use the official attendance dashboard as the structured source for the current
Parliament. Use the `parliament.mn/nc/635/` archive as provenance and for later
historical backfill. Do not infer individual statuses from screenshots when the
dashboard supplies a structured status.

## Overview

| Field | Value |
|---|---|
| Source ID | `parliament` |
| Organization | State Great Khural of Mongolia |
| Website | https://www.parliament.mn/nc/635/ |
| Structured dashboard | https://att.parliament.mn/ |
| Data type | HTML/embedded JSON + XLSX attachments |
| Update frequency | Per plenary sitting; records may be corrected later |
| Language | Mongolian source; party labels also include English |

## Authentication

No authentication is required. Fetch sequentially and keep the default delay;
the source is a public government service, not a bulk API.

## Pull Data

From the repository root:

```bash
uv run python .claude/skills/datamn-source-parliament/fetch_data.py
```

The pull writes normalized source files to
`tools/sources/parliament/raw/` by default:

- `parliament-members.csv` — current MP identity, party, mandate, district,
  committee, and official profile fields.
- `parliament-sessions.csv` — one row per plenary sitting, including scheduled
  and actual start times and status totals.
- `parliament-attendance.csv` — one row per MP per sitting, with the official
  status, arrival time, and minutes relative to both scheduled and actual start.
- `parliament-archive.csv` — the `nc/635` publication catalog for provenance and
  historical attachment discovery.
- `parliament-pull.meta.json` — pull time, coverage, counts, and source URLs.

Useful options:

```bash
# Fast structure check without fetching every sitting detail page
uv run python .claude/skills/datamn-source-parliament/fetch_data.py \
  --skip-session-details --skip-archive --skip-attachments \
  --output /tmp/parliament-check

# Reduce the polite delay only for local testing; do not add concurrency
uv run python .claude/skills/datamn-source-parliament/fetch_data.py --delay 0.1
```

## Status Semantics

Preserve Parliament's seven statuses separately:

| Source value | Meaning |
|---|---|
| `present` | Arrived on or before the dashboard's actual-start threshold |
| `late` | Arrived after that threshold |
| `excused_general` | Approved general leave |
| `excused_medical` | Medical leave |
| `mission_local` | Official domestic assignment |
| `mission_foreign` | Official foreign assignment |
| `absent_unexplained` | Unexplained absence / missed sitting |

Never collapse leave, official assignment, and unexplained absence into one
"absent" measure. Do not create a composite MP score.

## Punctuality Semantics

The official `present`/`late` distinction is relative to the recorded actual
start (or is provisional where Parliament flags it). The collector separately
calculates `minutes_from_scheduled_start`, which answers whether an MP was there
at the publicly scheduled time. These are different questions and must remain
separate in charts and prose.

If no scheduled or actual start was published, the corresponding derived field
is blank. Never substitute a default start time.

## Update Detection

Re-run the pull after each plenary sitting and periodically re-pull the current
term. Parliament's methodology says attendance can be updated through its
approved-leave workflow, so an incremental "new dates only" updater is unsafe.
The collector replaces the normalized snapshot only after all invariants pass.

## Build Public Views

After a successful pull, rebuild the two public child datasets and their
registry rows, then regenerate the bilingual workbooks:

```bash
uv run python tools/sources/parliament/build_public.py
uv run python tools/scripts/rebuild_downloads.py \
  --dataset mp-parliament-attendance --apply
uv run python tools/scripts/rebuild_downloads.py \
  --dataset parliament-session-attendance --apply
```

The public views deliberately keep physical attendance, official punctuality,
scheduled-start punctuality, approved leave, official assignments, and
unexplained absence separate. Do not introduce a composite ranking.

## Validation Invariants

The collector fails closed when:

- a new/unknown attendance status appears;
- the sitting dates in the list and member-history payload disagree;
- MPs do not have one record for every sitting;
- a sitting does not contain one record per current MP;
- the publication archive count does not match its reported total.

After a successful pull, inspect the metadata and run:

```bash
uv run python - <<'PY'
import csv, json
from pathlib import Path
p = Path('tools/sources/parliament/raw')
print(json.loads((p / 'parliament-pull.meta.json').read_text()))
for name in ('members', 'sessions', 'attendance', 'archive'):
    with (p / f'parliament-{name}.csv').open() as f:
        print(name, sum(1 for _ in csv.DictReader(f)))
PY
```

## Historical Backfill

The archive includes daily, monthly, and session-summary publications in mixed
formats (XLSX, images, and older documents). Backfill them as a separate phase:
download attachments, retain their article URL, and reconcile duplicate daily
and monthly reports. Do not merge an extracted historical row into the current
dashboard snapshot without recording its source document and status mapping.
