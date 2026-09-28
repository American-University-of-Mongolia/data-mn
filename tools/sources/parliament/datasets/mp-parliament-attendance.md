# Dataset: Attendance and Punctuality by Member of Parliament

## Identification

- **ID**: `mp-parliament-attendance`
- **Source**: `parliament`
- **Parent**: `parliament-attendance-records`
- **Category**: Government & Politics / Засаглал ба улс төр

## Purpose

Public current-Parliament view of physical attendance, unexplained absence,
approved leave, official assignment, and two separate punctuality baselines:
Parliament's actual-start classification and arrival by the scheduled start.

## Metrics

- Physical attendance rate: `present + late` divided by all sittings.
- Official on-time rate: `present` divided by `present + late`.
- Scheduled-start on-time rate: arrivals by the scheduled time divided by
  physical arrivals in sittings where a scheduled start was published.
- Unexplained absence rate: `absent_unexplained` divided by all sittings.
- Median and mean late minutes use official late arrivals with an actual start.

Leave and official assignments remain separate. No composite score is created.

## Build

```bash
uv run python tools/sources/parliament/build_public.py
uv run python tools/scripts/rebuild_downloads.py --dataset mp-parliament-attendance --apply
```

