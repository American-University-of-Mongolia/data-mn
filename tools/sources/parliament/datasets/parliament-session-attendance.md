# Dataset: Parliament Attendance by Plenary Sitting

## Identification

- **ID**: `parliament-session-attendance`
- **Source**: `parliament`
- **Parent**: `parliament-attendance-records`
- **Category**: Government & Politics / Засаглал ба улс төр

## Purpose

Public sitting-level view of attendance composition, agenda size, scheduled and
actual start times, start delay, data-finality state, and official source links.

## Status Groups Used in the Chart

- on time;
- late;
- approved leave (general + medical);
- official mission (domestic + foreign);
- unexplained absence.

The downloadable table retains the seven original statuses separately. Missing
start times are not imputed. Negative delay values are retained and flagged as
source anomalies rather than silently corrected.

## Build

```bash
uv run python tools/sources/parliament/build_public.py
uv run python tools/scripts/rebuild_downloads.py --dataset parliament-session-attendance --apply
```

