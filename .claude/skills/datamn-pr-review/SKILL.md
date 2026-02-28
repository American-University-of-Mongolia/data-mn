---
name: datamn-pr-review
description: "Validate and optionally merge/deploy PRs for data.mn. Checks only datasets added/modified in the PR."
---

# datamn-pr-review

Validate and optionally merge/deploy PRs for data.mn. Checks only datasets added/modified in the PR.

## Usage

```
/datamn-pr-review <pr_number>
```

## Workflow

### 1. Checkout PR

```bash
cd /home/ritz/projects/data
gh pr checkout <pr_number>
```

### 2. Detect Affected Datasets

Get list of files in the PR:
```bash
gh pr view <pr_number> --json files --jq '.files[].path'
```

Extract dataset IDs from paths matching:
- `data.mn/src/data/data/en/<dataset-id>.mdx`
- `data.mn/src/data/data/mn/<dataset-id>.mdx`

The dataset ID is the filename without `.mdx` extension.

### 3. Run Validations

For each detected dataset ID, run:
```bash
conda run -n datamn python tools/tests/run_all_checks.py <dataset-id>
```

Then run global checks:
```bash
# Chart validation
cd /home/ritz/projects/data/data.mn && python3 ../tools/scripts/validate_vega.py --all

# MDX validation
cd /home/ritz/projects/data && python3 tools/scripts/validate_mdx_datafiles.py

# Build
cd /home/ritz/projects/data/data.mn && npm run build

# Lint
cd /home/ritz/projects/data/data.mn && npm run check
```

### 4. Generate Report

Display results in this format:

```
╔═══════════════════════════════════════════════════════════════╗
║                PR #<N> VALIDATION REPORT                      ║
╠═══════════════════════════════════════════════════════════════╣
║ DATASETS (<count>):                                           ║
║   • <dataset-id>:  ✓ 85/85 passed  OR  ✗ X/85 failed         ║
║   • ...                                                       ║
╠═══════════════════════════════════════════════════════════════╣
║ CHARTS:      ✓ All valid       OR  ✗ N errors                ║
║ MDX FILES:   ✓ All valid       OR  ✗ N errors                ║
║ BUILD:       ✓ Succeeded       OR  ✗ Failed                  ║
║ LINT:        ✓ Passed          OR  ✗ Failed                  ║
╠═══════════════════════════════════════════════════════════════╣
║ RESULT:      ✓ READY TO MERGE  OR  ✗ NEEDS FIXES             ║
╚═══════════════════════════════════════════════════════════════╝
```

### 5. Decision Point

**If ALL checks pass:**
- Ask user: "All checks passed. Merge PR #<N> and deploy to data.mn?"
- If user approves:
  ```bash
  gh pr merge <pr_number> --squash --delete-branch
  cd /home/ritz/projects/data/data.mn && kamal deploy
  ```
- Confirm deployment complete

**If ANY check fails:**
- Post a GitHub comment to the PR with the validation report:
  ```bash
  gh pr comment <pr_number> --body "<report>"
  ```
- Return to main branch:
  ```bash
  cd /home/ritz/projects/data && git checkout main
  ```
- Tell user: "Posted feedback to PR #<N>. Returned to main branch."

## Error Handling

- If PR doesn't exist: "PR #<N> not found"
- If no datasets detected: Still run build/lint checks (may be code-only PR)
- If checkout fails: Report the git error

## Notes

- This runs on omarchy (hostname: ritz), so kamal deploy runs locally
- Dataset validation uses the `datamn` conda environment
- The `run_all_checks.py` script runs 85 validation checks per dataset
- Only datasets modified in the PR are validated (not all datasets in repo)
