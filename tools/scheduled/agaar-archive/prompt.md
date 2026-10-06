You are running the scheduled agaar.gov.mn archive job for data.mn, unattended.
Your working directory is a fresh git worktree of the data.mn repo on a new branch
created from origin/main. Nobody is watching: never ask questions, never decide
policy. Do the routine work, and write up anything that needs a human decision.

Why this job exists: agaar.gov.mn (NAMEM) drops hourly pollutant concentrations
once a month is validated. tools/sources/agaar/raw/ is the only long-term copy of
them, and fetch_data.py merges new data into it field by field so values are
never erased.

## Steps

1. Read .claude/skills/datamn-source-agaar/SKILL.md, tools/sources/agaar/source.md
   and tools/sources/agaar/pulls.md.
2. Copy tools/sources/agaar/raw/agaar-pulls.json to /tmp/agaar-pulls-before.json
   (your baseline).
3. Run the archive update (stdlib only, can take 30+ minutes; give the command a
   long timeout or run it in the background and wait for it):
       cd .claude/skills/datamn-source-agaar
       python3 fetch_data.py --output ../../../tools/sources/agaar/raw --update
   A nonzero exit means some station requests failed. Note which ones (the log
   and the manifest's stations_failed), but carry on.
4. Run the tests: `python3 -m unittest discover -s tests` in the skill directory.
5. Safety check. For every CSV under tools/sources/agaar/raw that git reports as
   changed, compare HEAD with the working copy and confirm that:
   - no (station_code, datetime|date) row that was in HEAD is missing, and
   - no pollutant value (pm10 pm25 o3 no2 co so2, plus pm10_24h pm25_24h hourly)
     that was non-empty in HEAD is now empty, unless that row has pm25_withheld=1
     (pm25/pm25_24h only).
   If anything was lost, or the tests fail: run `git checkout -- tools/sources/agaar`
   to discard the update, don't commit, and open a GitHub issue titled
   "agaar archive run <date>: <problem>" with the details (exact files, keys,
   counts). Then stop.
6. Compare the manifest with the baseline and look for things a human should
   decide on. Report them; do NOT act on them:
   - stations failing or newly returning no data, or stations that stopped
     reporting;
   - station codes in the data or on the site that aren't in
     .claude/skills/datamn-source-agaar/stations.json (catalog changes; check
     with `python3 query_api.py --list`);
   - new unavailable_days, or new kinds of server errors;
   - months that became validated (good: say so), and months nearing or reaching
     the 12-month cutoff while still unvalidated;
   - any sign the site changed: session key not found, new fields, empty replies,
     changed units or schema;
   - anything else surprising in the values (a station stuck at one value,
     impossible numbers).
   Do not edit the fetcher, the catalog, the registry, data.mn pages or any other
   dataset. If the fetcher is broken, describe the problem instead of fixing it.
7. Add a dated entry to tools/sources/agaar/pulls.md: one or two lines with the
   months fetched, rows and concentration rows added, newly validated months, and
   any findings.
8. Commit only tools/sources/agaar/ (data, manifest, pulls.md). End the commit
   message with:
       Co-Authored-By: Claude <noreply@anthropic.com>
   Push the branch and open a PR against main titled
   "agaar archive run <YYYY-MM-DD>". The PR body should have:
   - a short summary table: per re-fetched month and freq, rows before -> after,
     rows_with_concentrations before -> after, validated rows before -> after;
   - the safety check result (rows lost: 0, values lost: 0);
   - "## Decisions needed": a numbered list of the findings from step 6, each with
     the evidence and the options as you see them, or "None";
   - a final line: 🤖 Generated with [Claude Code](https://claude.com/claude-code)
9. Never merge the PR, never push to main, never deploy.

Finish with a short summary: the PR or issue URL, and whether any decisions are
needed.
