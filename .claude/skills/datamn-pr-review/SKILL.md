---
name: datamn-pr-review
description: Review a data.mn pull request. Use when asked to review, validate, or merge a PR. Checks only datasets added/modified in the PR, plus global checks, and prints a merge-ready report.
dependencies:
  - python3
  - sqlite3
  - gh
---

# datamn-pr-review

Review and optionally merge/deploy PRs for data.mn.

## Usage

```
Review PR #<N>
```

Run the review script (from the repo root, with the repo `.venv`):

```bash
cd /home/ritz/projects/data
.venv/bin/python tools/scripts/review_pr.py <N> --fast
```

Flags:

- `--fast` — skip slow steps (all-charts validation, build, lint). Good first pass.
- (no flags) — full validation including all charts. Run before merging.
- `--build` — also run `npm run build` in the PR worktree (slow, minutes).
- `--lint` — also run `npm run check` (astro + eslint + prettier).

## What the script does

1. Loads the PR head and changed-file list via the GitHub API.
2. Checks out the PR into a **temporary worktree** — the current working
   tree is never touched, and the worktree is removed afterwards.
3. Detects affected dataset IDs from changed
   `data.mn/src/data/data/{en,mn}/<id>.mdx` paths.
4. For each dataset runs, against the worktree copy:
   - `tools/tests/run_all_checks.py <id>` (file existence, frontmatter,
     CSV, charts, bilingual consistency, content quality)
   - `tools/scripts/validate_dataset.py --all <id>` (downloads, MDX body,
     chart-CSV consistency, registry sync)
5. Runs global checks: `validate_mdx_datafiles.py` and
   `validate_vega.py --all` (skipped with `--fast`), plus
   `validate_deprecation.py` scoped to datasets the PR touched
   (via MDX or registry-row changes) so unrelated issues don't block.
6. If `tools/registry/data.db` changed, prints a human-readable row diff
   of base vs PR (the DB is binary, otherwise unreviewable).
7. Prints a PASS/FAIL report with a READY TO MERGE / NEEDS FIXES verdict.

Exit code 0 means every executed check passed.

## After the report

**If ALL checks pass:**

- Ask the user: "All checks passed. Merge PR #\<N\> and deploy to data.mn?"
- If the user approves:
  ```bash
  gh pr merge <N> --squash --delete-branch
  ```
- Then deploy following the `deploy` skill
  (`data.mn/config/deploy.yml` uses the local-builder Kamal flow).
- Confirm deployment complete.

**If ANY check fails:**

- Post the report as a PR comment:
  ```bash
  gh pr comment <N> --body "<report>"
  ```
- Tell the user: "Posted feedback to PR #\<N\>."
- Do NOT merge. (No branch cleanup needed — the script uses temp worktrees.)

## Error handling

- If the PR doesn't exist: "PR #\<N\> not found".
- If no datasets detected: still run the global checks (may be a code-only PR).
- If fetch fails: report the git error.

## Notes

- This runs on omarchy (hostname: ritz), so deploys run locally.
- Python checks run with the repo `.venv` (`/home/ritz/projects/data/.venv`),
  which must include `pytest`, `pandas`, and `pyyaml`.
- Only datasets modified in the PR are validated per-dataset; global
  checks (MDX files, deprecation, charts) always cover the whole worktree.
- `npm run build` also regenerates chart thumbnails; a Fontconfig warning
  in containers without fonts is harmless (see root AGENTS.md).
