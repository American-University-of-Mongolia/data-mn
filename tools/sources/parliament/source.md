# Parliament Attendance — State Great Khural of Mongolia

## Source Information

- **ID**: `parliament`
- **Name**: State Great Khural of Mongolia
- **Name (MN)**: Монгол Улсын Их Хурал
- **Publication archive**: https://www.parliament.mn/nc/635/
- **Structured dashboard**: https://att.parliament.mn/
- **Type**: Mixed (HTML/embedded JSON + XLSX attachments)
- **Update frequency**: Per plenary sitting; corrections can follow later
- **Language**: Mongolian, with some English party metadata

## Scope

The structured dashboard covers plenary attendance for the current Parliament.
It supplies current MP metadata, every MP's status for every sitting, arrival
times, sitting-level totals, and scheduled/actual start times where published.

The main parliament.mn archive contains 400+ daily, monthly, and
session-summary attendance publications in mixed formats. It is retained as a
provenance catalog and historical-backfill source; it is not treated as a
single uniform table.

## Tooling

Use the `datamn-source-parliament` skill. Codex can run the project-local skill
wrapper from the repository root:

```bash
uv run python .agents/skills/datamn-source-parliament/scripts/fetch_data.py
```

Claude uses the same collector implementation directly at
`.claude/skills/datamn-source-parliament/fetch_data.py`.

Normalized pulls are written to `tools/sources/parliament/raw/`. The collector
is deliberately sequential, validates the full MP × sitting matrix, and only
replaces output files after the pull passes validation.

After the first successful pull, register the source and unpublished parent:

```bash
uv run python tools/sources/parliament/register.py
```

## Status Model

The source distinguishes:

- present/on time relative to the official actual-start threshold;
- late;
- approved general leave;
- medical leave;
- domestic official assignment;
- foreign official assignment;
- unexplained absence.

These statuses must remain separate. In particular, official assignment or
approved leave is not an unexplained absence.

## Timing Model

The source publishes both the time a sitting was scheduled and the time it
actually began for many sittings. The pull therefore preserves two distinct
punctuality views:

1. Parliament's official `present`/`late` classification relative to the
   actual-start threshold (occasionally flagged provisional).
2. A data.mn calculation of arrival minutes before/after the scheduled start.

No missing start time is imputed. The first view describes the official record;
the second answers whether MPs were present when the sitting was supposed to
begin.

## Update Rules

- Re-pull the entire current-term snapshot after new sittings.
- Do not use a new-dates-only update: approved leave/status corrections can
  change earlier rows.
- Fail closed on unknown statuses or an incomplete MP × sitting matrix.
- Keep the article/dashboard URL with each sitting for source verification.
- Reconcile archive attachments separately before historical records are
  appended to the normalized current-term parent.

## Output Files

| File | Grain | Purpose |
|---|---|---|
| `raw/parliament-members.csv` | MP | Names, party, district/mandate, committee, profile |
| `raw/parliament-sessions.csv` | Sitting | Date, session type, schedule/start, status totals |
| `raw/parliament-attendance.csv` | MP × sitting | Status, arrival, scheduled/actual timing deltas |
| `raw/parliament-archive.csv` | Publication | Historical archive catalog and article URL |
| `raw/parliament-pull.meta.json` | Pull | Provenance, coverage, counts, status totals |
