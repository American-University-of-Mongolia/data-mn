# Dataset: Parliament Attendance Records

## Identification

- **ID**: `parliament-attendance-records`
- **Source**: `parliament`
- **Category**: Government & Politics / Засаглал ба улс төр
- **Tags**: [parliament, attendance, punctuality, MPs, plenary]
- **Parent**: yes — raw normalized source; never publish directly

## Title

- **EN**: Mongolian Parliament Plenary Attendance Records
- **MN**: Монгол Улсын Их Хурлын нэгдсэн хуралдааны ирцийн бүртгэл

## Description

One normalized record per Member of Parliament per plenary sitting, joined to
current MP and sitting metadata. It preserves Parliament's seven attendance
statuses and distinguishes official lateness (relative to the actual-start
threshold) from arrival relative to the publicly scheduled start.

## Source Files

- `tools/sources/parliament/raw/parliament-members.csv`
- `tools/sources/parliament/raw/parliament-sessions.csv`
- `tools/sources/parliament/raw/parliament-attendance.csv`
- `tools/sources/parliament/raw/parliament-archive.csv`
- `tools/sources/parliament/raw/parliament-pull.meta.json`

## Variables

### Attendance grain (MP × sitting)

- `session_id`, `date`, `member_id` — stable join keys.
- `status` — one of the seven official statuses documented in `source.md`.
- `arrival_time` — source-recorded arrival time when applicable.
- `official_arrival_class` — on time/late according to Parliament's threshold.
- `scheduled_arrival_class` — on time/late relative to the scheduled start.
- `minutes_from_scheduled_start` — negative is early, positive is late.
- `minutes_from_actual_start` — negative is before actual start, positive after.
- `late_provisional` — Parliament's indicator that the lateness basis may change.

### Sitting grain

- scheduled and actual start time and the start delay in minutes;
- parliamentary year/session kind and agenda count;
- counts for each official status;
- source dashboard, article, and attachment URLs when published.

### MP grain

- Mongolian name, party (MN/EN), district or list mandate, committee, official
  profile, and photo URL.

## Planned User-Facing Splits

### `mp-parliament-attendance`

Per-MP attendance and punctuality over a selected period: physical attendance,
unexplained absence, approved leave and assignment counts, scheduled-time
punctuality, official on-time rate, and median lateness. No composite ranking.

### `parliament-session-attendance`

Per-sitting attendance: scheduled versus actual start delay, status composition,
on-time/late arrivals, agenda count, and links back to the official record.

## Update Instructions

```bash
uv run python .agents/skills/datamn-source-parliament/scripts/fetch_data.py
```

Rebuild both public splits from the full refreshed parent snapshot. Do not append
only new dates because Parliament can revise prior statuses.
